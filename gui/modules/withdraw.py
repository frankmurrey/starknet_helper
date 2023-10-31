import customtkinter
from tkinter import messagebox
from typing import Callable, Union
from pydantic.error_wrappers import ValidationError

from loguru import logger

from src import enums
from src.schemas import tasks
from contracts.tokens.main import Tokens
from gui.modules.txn_settings_frame import TxnSettingFrame


WITHDRAW_TASKS = {
    enums.ModuleName.ZKLEND: tasks.ZkLendWithdrawTask
}


class WithdrawLendingTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.WithdrawTaskBase = None
    ):
        self.tabview = tabview

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        withdraw_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.withdraw_frame = WithdrawLendingFrame(
            master=self.tabview.tab(tab_name),
            grid=withdraw_frame_grid,
            task=task
        )

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid={
                "row": 1,
                "column": 0,
                "padx": 20,
                "pady": 20,
                "sticky": "nsew"
            },
            task=task
        )

    def get_config_schema(self) -> Union[Callable, None]:
        protocol = self.withdraw_frame.protocol_combobox.get().lower()
        return WITHDRAW_TASKS.get(protocol, None)

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            return config_schema(
                coin_to_withdraw=self.withdraw_frame.token_to_withdraw_combobox.get(),
                max_fee=self.txn_settings_frame.max_fee_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
            )
        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class WithdrawLendingFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task: tasks.WithdrawTaskBase = None
    ):
        super().__init__(master)

        self.grid(**grid)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # PROTOCOL
        self.protocol_label = customtkinter.CTkLabel(
            master=self,
            text="Protocol"
        )
        self.protocol_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        protocol = getattr(task, "protocol", self.protocol_options[0])
        self.protocol_combobox = customtkinter.CTkComboBox(
            master=self,
            values=self.protocol_options,
            width=120,
            command=self.protocol_change_event
        )
        self.protocol_combobox.set(protocol.upper())
        self.protocol_combobox.grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # TOKEN TO WITHDRAW
        self.token_to_withdraw = customtkinter.CTkLabel(
            master=self,
            text="Token to Supply"
        )
        self.token_to_withdraw.grid(
            row=2,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        coin_to_withdraw = getattr(task, "coin_to_withdraw", self.protocol_coin_options[0])
        self.token_to_withdraw_combobox = customtkinter.CTkComboBox(
            master=self,
            values=self.protocol_coin_options,
            width=120
        )
        self.token_to_withdraw_combobox.set(coin_to_withdraw.upper())
        self.token_to_withdraw_combobox.grid(
            row=3,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 20)
        )

    @property
    def protocol_options(self) -> list:
        return [
            enums.ModuleName.ZKLEND.upper()
        ]

    @property
    def protocol_coin_options(self) -> list:
        tokens = Tokens()
        protocol = self.protocol_combobox.get()
        return [token.symbol.upper() for token in tokens.get_tokens_by_protocol(protocol)]

    def protocol_change_event(self, protocol=None):
        coin_to_supply_options = self.protocol_coin_options
        self.token_to_withdraw_combobox.configure(values=coin_to_supply_options)
        self.token_to_withdraw_combobox.set(coin_to_supply_options[1])