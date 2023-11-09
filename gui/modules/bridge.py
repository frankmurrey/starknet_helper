from tkinter import messagebox
from typing import Union, Callable

import customtkinter
from pydantic.error_wrappers import ValidationError
from tkinter import Variable
from loguru import logger

from gui.modules.txn_settings_frame import TxnSettingFrame
from gui import constants
from contracts.tokens.main import Tokens
from contracts.chains.main import Chains
from src import enums
from src.schemas import tasks
from src.schemas.data_models import OrbiterChainData
from utils.orbiter_utils import get_orbiter_bridge_data_by_token


BRIDGE_TASKS = {
    enums.ModuleName.ORBITER: tasks.OrbiterBridgeTask,
    enums.ModuleName.STARK_BRIDGE: tasks.StarkBridgeTask,
}


class BridgeTab:
    def __init__(self, tabview, tab_name, task: tasks.BridgeTaskBase = None):
        self.tabview = tabview
        self.tab_name = tab_name

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        bridge_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.bridge_frame = BridgeFrame(
            master=self.tabview.tab(tab_name),
            grid=bridge_frame_grid,
            task=task
        )

        txn_settings_frame_grid = {
                "row": 1,
                "column": 0,
                "padx": 20,
                "pady": 20,
                "sticky": "nsew"
            }

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid=txn_settings_frame_grid
        )

    def get_config_schema(self) -> Union[Callable, None]:
        protocol = self.bridge_frame.protocol_combobox.get().lower()

        return BRIDGE_TASKS.get(protocol, None)

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        chain_data = self.bridge_frame.get_current_chain_data()

        min_amount_out = self.bridge_frame.min_amount_out_entry.get()
        max_amount_out = self.bridge_frame.max_amount_out_entry.get()

        try:
            task = config_schema(
                coin_x=self.bridge_frame.coin_combobox.get(),
                dst_chain=self.bridge_frame.chain_combobox.get(),
                min_amount_out=min_amount_out,
                max_amount_out=max_amount_out,
                use_all_balance=self.bridge_frame.use_all_balance_checkbox.get(),
                send_percent_balance=self.bridge_frame.send_percent_balance_checkbox.get(),
                max_fee=self.txn_settings_frame.max_fee_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
            )

            if chain_data:
                if (not self.bridge_frame.use_all_balance_checkbox.get() and
                        not self.bridge_frame.send_percent_balance_checkbox.get()):

                    if float(min_amount_out) < chain_data.minPrice + chain_data.tradingFee:
                        messagebox.showerror(
                            title="Error",
                            message=f"Min amount out must be greater than {chain_data.minPrice + chain_data.tradingFee}, "
                                    f"(min amount + fee)"
                        )
                        return None

                    if float(max_amount_out) > chain_data.maxPrice:
                        messagebox.showerror(
                            title="Error",
                            message=f"Max amount out must be less than {chain_data.maxPrice}"
                        )
                        return None

            return task

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class BridgeFrame(customtkinter.CTkFrame):
    def __init__(self, master, grid, task: tasks.BridgeTaskBase, **kwargs):
        super().__init__(master, **kwargs)

        self.grid(**grid)
        self.grid_columnconfigure((0, 1), weight=1, uniform="a")
        self.grid_rowconfigure((1, 2, 3, 4, 5, 6, 7), weight=1)

        self.task = task
        self.chains = Chains()
        self.tokens = Tokens()

        # PROTOCOL
        self.protocol_label = customtkinter.CTkLabel(
            master=self,
            text="Protocol:"
        )
        self.protocol_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        self.protocol_combobox = customtkinter.CTkComboBox(
            master=self,
            values=self.protocol_options,
            width=120,
            command=self.protocol_change_event
        )

        protocol = getattr(self.task, "module_name", self.protocol_options[0])
        self.protocol_combobox.set(protocol.upper())
        self.protocol_combobox.grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # DEST CHAIN
        self.chain_label = customtkinter.CTkLabel(
            master=self,
            text="Dest chain:"
        )
        self.chain_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        self.chain_combobox = customtkinter.CTkComboBox(
            master=self,
            values=self.chain_options,
            width=120,
            command=self.chain_change_event
        )
        self.chain_combobox.set(getattr(task, "dst_chain", self.chain_options[0]))
        self.chain_combobox.grid(
            row=3,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # COIN
        self.coin_label = customtkinter.CTkLabel(
            master=self,
            text="Coin to bridge:"
        )
        self.coin_label.grid(
            row=2,
            column=1,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        self.coin_combobox = customtkinter.CTkComboBox(
            master=self,
            values=self.coin_options,
            width=120,
            command=self.coin_change_event
        )
        self.coin_combobox.set(getattr(task, "coin_x", self.coin_options[0]))
        self.coin_combobox.grid(
            row=3,
            column=1,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        self.bridge_data_frame = BridgeDataFrame(
            master=self,
            chain_data=self.get_current_chain_data(),
            grid={
                "row": 4,
                "column": 0,
                "padx": 20,
                "pady": (20, 10),
                "sticky": "nsew"
            }
        )

        # MIN AMOUNT OUT
        self.min_amount_out_label = customtkinter.CTkLabel(
            master=self,
            text="Min amount out:"
        )
        self.min_amount_out_label.grid(
            row=5,
            column=0,
            sticky="w",
            padx=20,
            pady=0
        )

        min_amount_out = getattr(task, "min_amount_out", "")
        self.min_amount_out_entry = customtkinter.CTkEntry(
            master=self,
            width=120,
            textvariable=Variable(value=min_amount_out)
        )
        self.min_amount_out_entry.grid(
            row=6,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # MAX AMOUNT OUT
        self.max_amount_out_label = customtkinter.CTkLabel(
            master=self,
            text="Max amount out:"
        )
        self.max_amount_out_label.grid(
            row=5,
            column=1,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        max_amount_out = getattr(task, "max_amount_out", "")
        self.max_amount_out_entry = customtkinter.CTkEntry(
            master=self,
            width=120,
            textvariable=Variable(value=max_amount_out)
        )
        self.max_amount_out_entry.grid(
            row=6,
            column=1,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # USE ALL BALANCE
        self.use_all_balance_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Use All Balance",
            checkbox_width=18,
            checkbox_height=18,
            command=self.use_all_balance_checkbox_event
        )
        self.use_all_balance_checkbox.grid(
            row=7,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        self.send_percent_balance_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Send Percent Balance",
            checkbox_width=18,
            checkbox_height=18
        )
        self.send_percent_balance_checkbox.grid(
            row=8,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 20)
        )
        if getattr(self.task, "send_percent_balance", False):
            self.send_percent_balance_checkbox.select()

        if getattr(self.task, "use_all_balance", False):
            self.use_all_balance_checkbox.select()
            self.min_amount_out_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_out_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(
                state="disabled"
            )

    @property
    def protocol_options(self) -> list:
        return [name.upper() for name in BRIDGE_TASKS.keys()]

    @property
    def chain_options(self) -> list:
        if self.protocol_combobox.get() == enums.ModuleName.ORBITER.upper():
            return [chain.name.upper() for chain in self.chains.all_chains if chain.orbiter_id is not None]

        elif self.protocol_combobox.get() == enums.ModuleName.STARK_BRIDGE.upper():
            return ["Ethereum"]

        else:
            raise NotImplementedError

    @property
    def coin_options(self) -> list:
        chain = self.chains.get_by_name(self.chain_combobox.get())

        if self.protocol_combobox.get() == enums.ModuleName.ORBITER.upper():
            return [token.upper() for token in chain.orbiter_supported_tokens]

        elif self.protocol_combobox.get() == enums.ModuleName.STARK_BRIDGE.upper():
            return ["ETH"]

        else:
            raise NotImplementedError

    def get_current_chain_data(self) -> Union[OrbiterChainData, None]:
        if self.protocol_combobox.get() == enums.ModuleName.ORBITER.upper():
            return get_orbiter_bridge_data_by_token(
                chain_id=self.chains.get_by_name(self.chain_combobox.get()).orbiter_id,
                token_symbol=self.coin_combobox.get()
            )

        else:
            return None

    def protocol_change_event(self, value: str):
        chain_options = self.chain_options
        self.chain_combobox.configure(values=chain_options)
        self.chain_combobox.set(chain_options[0])

        coin_options = self.coin_options
        self.coin_combobox.configure(values=coin_options)
        self.coin_combobox.set(coin_options[0])

        self.bridge_data_frame.update_data(chain_data=self.get_current_chain_data())

    def chain_change_event(self, chain: str):
        coin_options = self.coin_options
        self.coin_combobox.configure(values=coin_options)
        self.coin_combobox.set(coin_options[0])

        chain_data = get_orbiter_bridge_data_by_token(
            chain_id=self.chains.get_by_name(chain).orbiter_id,
            token_symbol=self.coin_combobox.get()
        )

        self.bridge_data_frame.update_data(chain_data=chain_data)

    def coin_change_event(self, coin: str):
        chain_data = get_orbiter_bridge_data_by_token(
            chain_id=self.chains.get_by_name(self.chain_combobox.get()).orbiter_id,
            token_symbol=coin
        )

        self.bridge_data_frame.update_data(chain_data=chain_data)

    def use_all_balance_checkbox_event(self):
        if self.use_all_balance_checkbox.get():
            self.min_amount_out_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_out_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(
                state="disabled"
            )
        else:
            self.min_amount_out_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value="")
            )
            self.max_amount_out_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.configure(
                state="normal"
            )


class BridgeDataFrame(customtkinter.CTkFrame):
    def __init__(self, master, chain_data: OrbiterChainData, grid, **kwargs):
        super().__init__(master, **kwargs)

        self.grid(columnspan=2, **grid)
        self.grid_columnconfigure((0, 1), weight=0, uniform="a")
        self.grid_rowconfigure((0, 1, 2), weight=0)

        self.chain_data = chain_data

        self.min_price_label = customtkinter.CTkLabel(
            master=self,
            text=f"Min amount:",
            text_color=constants.SUCCESS_HEX
        )
        self.min_price_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(20, 20),
            pady=(5, 0)
        )

        min_price = getattr(self.chain_data, "minPrice", "-")
        self.min_price_value_label = customtkinter.CTkLabel(
            master=self,
            text=str(min_price),
            text_color=constants.SUCCESS_HEX
        )
        self.min_price_value_label.grid(
            row=0,
            column=1,
            sticky="w",
            padx=(0, 20),
            pady=(5, 0)
        )

        self.max_price_label = customtkinter.CTkLabel(
            master=self,
            text=f"Max amount:",
            text_color=constants.ERROR_HEX
        )
        self.max_price_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=(20, 20),
            pady=0
        )

        max_price = getattr(self.chain_data, "maxPrice", "-")
        self.max_price_value_label = customtkinter.CTkLabel(
            master=self,
            text=str(max_price),
            text_color=constants.ERROR_HEX
        )
        self.max_price_value_label.grid(
            row=1,
            column=1,
            sticky="w",
            padx=(0, 20),
            pady=0
        )

        self.trading_fee_label = customtkinter.CTkLabel(
            master=self,
            text=f"Fee:",
            text_color=constants.ORANGE_HEX
        )
        self.trading_fee_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=(20, 20),
            pady=(0, 5)
        )

        fee = getattr(self.chain_data, "tradingFee", "-")
        self.trading_fee_value_label = customtkinter.CTkLabel(
            master=self,
            text=str(fee),
            text_color=constants.ORANGE_HEX
        )
        self.trading_fee_value_label.grid(
            row=2,
            column=1,
            sticky="w",
            padx=(0, 20),
            pady=(0, 5)
        )

    def update_data(self, chain_data: OrbiterChainData):
        self.chain_data = chain_data

        min_p, max_p, fee = "-", "-", "-"
        if chain_data:
            min_p, max_p, fee = map(str, [chain_data.minPrice, chain_data.maxPrice, chain_data.tradingFee])

        self.min_price_value_label.configure(text=min_p)
        self.max_price_value_label.configure(text=max_p)
        self.trading_fee_value_label.configure(text=fee)
