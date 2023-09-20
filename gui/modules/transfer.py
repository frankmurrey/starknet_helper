from typing import Callable
from typing import Union
from tkinter import messagebox

import customtkinter
from pydantic.error_wrappers import ValidationError
from tkinter import Variable
from loguru import logger

from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.objects import CTkEntryWithLabel
from contracts.tokens.main import Tokens
from src.schemas.tasks.transfer import TransferTask


class TransferTab:
    def __init__(self, tabview, tab_name):
        self.tabview = tabview

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        transfer_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.transfer_frame = TransferFrame(master=self.tabview.tab(tab_name), grid=transfer_frame_grid)

        txn_settings_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name), grid=txn_settings_grid
        )

    def build_config_data(self):
        config_schema = TransferTask

        try:
            config_data = config_schema(
                coin_x=self.transfer_frame.coin_x_combobox.get(),
                min_amount_out=self.transfer_frame.min_amount_out_element.entry.get(),
                max_amount_out=self.transfer_frame.max_amount_out_element.entry.get(),
                use_all_balance=self.transfer_frame.use_all_balance_checkbox.get(),
                max_fee=self.txn_settings_frame.max_fee_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
                send_percent_balance=self.transfer_frame.send_percent_balance_checkbox.get(),

            )
            return config_data

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class TransferFrame(customtkinter.CTkFrame):
    def __init__(self, master, grid, **kwargs):
        super().__init__(master, **kwargs)

        self.grid(**grid)
        self.columnconfigure(0, weight=1)

        self.coin_x_label = customtkinter.CTkLabel(
            self,
            text="Coin to transfer:",
        )
        self.coin_x_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 0))

        self.coin_x_combobox = customtkinter.CTkComboBox(
            self,
            values=self.coin_options,
            width=120,
        )
        self.coin_x_combobox.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 0))

        self.min_amount_out_element = CTkEntryWithLabel(
            self,
            label_text="Min amount out:",
            width=120,
        )
        self.min_amount_out_element.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 0))

        self.max_amount_out_element = CTkEntryWithLabel(
            self,
            label_text="Max amount out:",
            width=120,
        )
        self.max_amount_out_element.grid(row=2, column=1, sticky="e", padx=20, pady=(10, 0))

        self.use_all_balance_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Use all balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.use_all_balance_checkbox_event,
        )
        self.use_all_balance_checkbox.grid(row=3, column=0, sticky="w", padx=20, pady=(10, 0))

        self.send_percent_balance_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Send % of balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
        )
        self.send_percent_balance_checkbox.grid(row=4, column=0, sticky="w", padx=20, pady=(10, 20))

    @property
    def coin_options(self) -> list:
        tokens = Tokens().all_tokens
        return [token.symbol.upper() for token in tokens]

    def use_all_balance_checkbox_event(self):
        if self.use_all_balance_checkbox.get():
            self.min_amount_out_element.entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )
            self.max_amount_out_element.entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(state="disabled")
        else:
            self.min_amount_out_element.entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value="")
            )
            self.max_amount_out_element.entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.configure(state="normal")





