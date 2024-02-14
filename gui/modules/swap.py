from typing import Callable
from typing import Union
from tkinter import messagebox

import customtkinter
from pydantic.error_wrappers import ValidationError
from tkinter import Variable
from loguru import logger

from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.objects import ComboWithRandomCheckBox
from contracts.tokens.main import Tokens
from src import enums
from src.schemas import tasks


SWAP_TASKS = {
    enums.ModuleName.JEDI_SWAP: tasks.JediSwapTask,
    enums.ModuleName.SITHSWAP: tasks.SithSwapTask,
    enums.ModuleName.MY_SWAP: tasks.MySwapTask,
    enums.ModuleName.AVNU: tasks.AvnuSwapTask,
    enums.ModuleName.K10SWAP: tasks.K10SwapTask,
    enums.ModuleName.FIBROUS: tasks.FibrousSwapTask,
    enums.ModuleName.STARKEX: tasks.StarkExSwapTask,
}


class SwapTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.SwapTaskBase = None
    ):
        self.tabview = tabview
        self.tab_name = tab_name

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        swap_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": (10, 0),
            "sticky": "nsew",
        }

        self.swap_frame = SwapFrame(
            master=self.tabview.tab(tab_name),
            grid=swap_frame_grid,
            task=task
        )

        txn_settings_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid=txn_settings_grid,
            task=task
        )

    def get_config_schema(self) -> Union[Callable, None]:
        protocol = self.swap_frame.protocol_combo.get_value().lower()
        if self.swap_frame.protocol_combo.get_checkbox_value():
            return tasks.RandomSwapTask

        else:
            return SWAP_TASKS.get(protocol, None)

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            config_data: tasks.SwapTaskBase = config_schema(
                coin_x=self.swap_frame.coin_to_swap_combo.get(),
                coin_y=self.swap_frame.coin_to_receive_combo.combobox.get(),
                random_y_coin=self.swap_frame.coin_to_receive_combo.get_checkbox_value(),
                min_amount_out=self.swap_frame.min_amount_entry.get(),
                max_amount_out=self.swap_frame.max_amount_entry.get(),
                use_all_balance=self.swap_frame.use_all_balance_checkbox.get(),
                send_percent_balance=self.swap_frame.send_percent_balance_checkbox.get(),
                reverse_action=self.swap_frame.reverse_action_checkbox.get(),
                slippage=self.swap_frame.slippage_entry.get(),
                max_price_difference_percent=self.swap_frame.max_price_difference_percent_entry.get(),
                compare_with_cg_price=self.swap_frame.compare_with_cg_price_checkbox.get(),
                max_fee=self.txn_settings_frame.max_fee_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
                reverse_action_min_delay_sec=self.swap_frame.reverse_action_min_delay_entry.get(),
                reverse_action_max_delay_sec=self.swap_frame.reverse_action_max_delay_entry.get(),
            )

            return config_data

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class SwapFrame(customtkinter.CTkFrame):
    def __init__(self, master, grid, task: tasks.SwapTaskBase):
        super().__init__(master)

        self.task = task

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(**grid)
        self.frame.grid_columnconfigure((0, 1), weight=1, uniform="a")
        self.frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

        # PROTOCOL
        self.protocol_label = customtkinter.CTkLabel(self.frame, text="Protocol:")
        self.protocol_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")

        self.protocol_combo = ComboWithRandomCheckBox(
            self.frame,
            grid={"row": 1, "column": 0, "padx": 20, "pady": 0, "sticky": "w"},
            options=self.protocol_options,
            combo_command=self.protocol_change_event,
            text="Random protocol",
        )
        protocol = getattr(self.task, "module_name", self.protocol_options[0])
        self.protocol_combo.set_values(
            combo_value=protocol.upper(),
        )

        # COIN TO SWAP
        self.coin_to_swap_label = customtkinter.CTkLabel(
            self.frame, text="Coin to swap:"
        )
        self.coin_to_swap_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")

        self.coin_to_swap_combo = customtkinter.CTkComboBox(
            self.frame,
            values=self.coin_to_swap_options,
            width=120,
            command=self.update_coin_options,
        )
        self.coin_to_swap_combo.set(getattr(self.task, "coin_x", self.coin_to_swap_options[0]))
        self.coin_to_swap_combo.grid(row=4, column=0, padx=20, pady=0, sticky="w")

        # COIN TO RECEIVE
        self.coin_to_receive_label = customtkinter.CTkLabel(
            self.frame, text="Coin to receive:"
        )
        self.coin_to_receive_label.grid(
            row=3, column=1, padx=20, pady=(10, 0), sticky="w"
        )

        self.coin_to_receive_combo = ComboWithRandomCheckBox(
            self.frame,
            grid={"row": 4, "column": 1, "padx": 20, "pady": 0, "sticky": "w"},
            options=self.coin_to_receive_options,
            text="Random dst coin",
        )
        self.coin_to_receive_combo.set_values(
            combo_value=getattr(self.task, "coin_y", self.coin_to_receive_options[0]),
        )

        # REVERSE ACTION CHECKBOX
        self.reverse_action_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Make reverse swap",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.reverse_action_checkbox_event
        )
        if getattr(self.task, "reverse_action", False):
            self.reverse_action_checkbox.select()

        self.reverse_action_checkbox.grid(
            row=5, column=0, padx=20, pady=(10, 0), sticky="w"
        )

        # REVERSE ACTION MIN DELAY
        self.reverse_action_min_delay_label = customtkinter.CTkLabel(
            self.frame, text="Reverse min delay (s):"
        )
        self.reverse_action_min_delay_label.grid(
            row=6, column=0, padx=20, pady=(10, 0), sticky="w"
        )

        is_reverse_action = getattr(self.task, "reverse_action", False)
        reverse_action_min_delay = getattr(self.task, "reverse_action_min_delay_sec", 1)
        self.reverse_action_min_delay_entry = customtkinter.CTkEntry(
            self.frame,
            width=120,
            textvariable=Variable(value=reverse_action_min_delay) if is_reverse_action else Variable(value=""),
            fg_color="#343638" if is_reverse_action else "#3f3f3f",
            state="disabled" if not is_reverse_action else "normal",
        )
        self.reverse_action_min_delay_entry.grid(
            row=7, column=0, padx=20, pady=0, sticky="w"
        )

        # REVERSE ACTION MAX DELAY
        self.reverse_action_max_delay_label = customtkinter.CTkLabel(
            self.frame, text="Reverse max delay (s):"
        )
        self.reverse_action_max_delay_label.grid(
            row=6, column=1, padx=20, pady=(10, 0), sticky="w"
        )

        reverse_action_max_delay = getattr(self.task, "reverse_action_max_delay_sec", 5)
        self.reverse_action_max_delay_entry = customtkinter.CTkEntry(
            self.frame,
            width=120,
            textvariable=Variable(value=reverse_action_max_delay) if is_reverse_action else Variable(value=""),
            fg_color="#343638" if is_reverse_action else "#3f3f3f",
            state="disabled" if not is_reverse_action else "normal",
        )
        self.reverse_action_max_delay_entry.grid(
            row=7, column=1, padx=20, pady=0, sticky="w"
        )

        # MIN AMOUNT
        self.min_amount_label = customtkinter.CTkLabel(self.frame, text="Min amount:")
        self.min_amount_label.grid(row=8, column=0, padx=20, pady=(10, 0), sticky="w")

        min_amount = getattr(self.task, "min_amount_out", "")
        self.min_amount_entry = customtkinter.CTkEntry(self.frame, width=120, textvariable=Variable(value=min_amount))
        self.min_amount_entry.grid(row=9, column=0, padx=20, pady=0, sticky="w")

        # MAX AMOUNT
        self.max_amount_label = customtkinter.CTkLabel(self.frame, text="Max amount:")
        self.max_amount_label.grid(row=8, column=1, padx=20, pady=(10, 0), sticky="w")

        max_amount = getattr(self.task, "max_amount_out", "")
        self.max_amount_entry = customtkinter.CTkEntry(self.frame, width=120, textvariable=Variable(value=max_amount))
        self.max_amount_entry.grid(row=9, column=1, padx=20, pady=0, sticky="w")

        self.use_all_balance_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Use all balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.use_all_balance_checkbox_event,
        )

        self.use_all_balance_checkbox.grid(
            row=10, column=0, padx=20, pady=(10, 0), sticky="w"
        )

        self.send_percent_balance_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Send % of balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
        )
        self.send_percent_balance_checkbox.grid(
            row=11, column=0, padx=20, pady=(5, 0), sticky="w"
        )
        if getattr(self.task, "send_percent_balance", False):
            self.send_percent_balance_checkbox.select()

        if getattr(self.task, "use_all_balance", False):
            self.use_all_balance_checkbox.select()
            self.min_amount_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(
                state="disabled"
            )

        self.slippage_label = customtkinter.CTkLabel(self.frame, text="Slippage (%):")
        self.slippage_label.grid(row=12, column=1, padx=20, pady=(10, 0), sticky="w")

        slippage = getattr(self.task, "slippage", 2)
        self.slippage_entry = customtkinter.CTkEntry(
            self.frame, width=70, textvariable=Variable(value=slippage)
        )
        self.slippage_entry.grid(row=13, column=1, padx=20, pady=0, sticky="w")

        self.max_price_difference_percent_label = customtkinter.CTkLabel(
            self.frame, text="Max price difference (%):"
        )
        self.max_price_difference_percent_label.grid(
            row=12, column=0, padx=20, pady=(10, 0), sticky="w"
        )

        max_price_difference_percent = getattr(self.task, "max_price_difference_percent", 2)
        self.max_price_difference_percent_entry = customtkinter.CTkEntry(
            self.frame, width=120, textvariable=Variable(value=max_price_difference_percent)
        )
        self.max_price_difference_percent_entry.grid(
            row=13, column=0, padx=20, pady=0, sticky="w"
        )

        self.compare_with_cg_price_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Compare to Gecko price",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.compare_with_cg_price_checkbox_event,
        )

        if getattr(self.task, "compare_with_cg_price", True):
            self.compare_with_cg_price_checkbox.select()
            self.max_price_difference_percent_entry.configure(
                state='normal', textvariable=max_price_difference_percent
            )
        else:
            self.max_price_difference_percent_entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )

        self.compare_with_cg_price_checkbox.grid(
            row=14, column=0, padx=20, pady=10, sticky="w"
        )
        self.compare_with_cg_price_checkbox.select()

    @property
    def protocol_options(self) -> list:
        return [name.upper() for name in SWAP_TASKS.keys()]

    @property
    def protocol_coin_options(self) -> list:
        tokens = Tokens()
        protocol = self.protocol_combo.get_value()

        return [
            token.symbol.upper() for token in tokens.get_tokens_by_protocol(protocol)
        ]

    @property
    def coin_to_swap_options(self) -> list:
        if self.protocol_combo.get_checkbox_value():
            coins = Tokens().general_tokens
            coin_symbols = [coin.symbol.upper() for coin in coins]
        else:
            coin_symbols = self.protocol_coin_options

        return coin_symbols

    @property
    def coin_to_receive_options(self) -> list:

        if self.protocol_combo.get_checkbox_value():
            coins = Tokens().general_tokens
            coin_symbols = [coin.symbol.upper() for coin in coins]

        else:
            protocol_coin_options = self.protocol_coin_options
            coin_to_swap = self.coin_to_swap_combo.get().lower()
            coin_symbols = [
                coin.upper()
                for coin in protocol_coin_options
                if coin.lower() != coin_to_swap.lower()
            ]

        return coin_symbols

    def reverse_action_checkbox_event(self):
        if self.reverse_action_checkbox.get():
            self.reverse_action_min_delay_entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value=1)
            )
            self.reverse_action_max_delay_entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value=5)
            )
        else:
            self.reverse_action_min_delay_entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )
            self.reverse_action_max_delay_entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )

    def update_coin_options(self, event=None):
        coin_to_swap_options = self.coin_to_swap_options
        self.coin_to_swap_combo.configure(values=coin_to_swap_options)

        coin_to_receive_options = self.coin_to_receive_options
        self.coin_to_receive_combo.combobox.configure(values=coin_to_receive_options)
        self.coin_to_receive_combo.combobox.set(coin_to_receive_options[1])

    def protocol_change_event(self, protocol=None):
        coin_to_swap_options = self.coin_to_swap_options
        self.coin_to_swap_combo.configure(values=coin_to_swap_options)
        self.coin_to_swap_combo.set(coin_to_swap_options[1])

        coin_to_receive_options = self.coin_to_receive_options
        self.coin_to_receive_combo.combobox.configure(values=coin_to_receive_options)
        self.coin_to_receive_combo.combobox.set(coin_to_receive_options[1])

    def use_all_balance_checkbox_event(self):
        if self.use_all_balance_checkbox.get():
            self.min_amount_entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(state="disabled")
        else:
            self.min_amount_entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.configure(state="normal")

    def compare_with_cg_price_checkbox_event(self):
        if self.compare_with_cg_price_checkbox.get():
            self.max_price_difference_percent_entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value=2)
            )
        else:
            self.max_price_difference_percent_entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )
