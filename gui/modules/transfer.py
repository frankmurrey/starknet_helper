from tkinter import messagebox

import customtkinter
from pydantic.error_wrappers import ValidationError
from tkinter import Variable

from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.objects import CTkEntryWithLabel
from gui.objects import CTkCustomTextBox
from contracts.tokens.main import Tokens
from src.schemas import tasks


class TransferTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.TransferTask = None
    ):
        self.tabview = tabview

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        transfer_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.transfer_frame = TransferFrame(
            master=self.tabview.tab(tab_name),
            grid=transfer_frame_grid,
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

        text_box_grid = {
            "row": 2,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "ew"
        }

        text = f"- Recipient should be set in the wallet settings as 'Pair address'."

        self.info_textbox = CTkCustomTextBox(
            master=self.tabview.tab(tab_name),
            grid=text_box_grid,
            text=text,
        )

    def build_config_data(self):
        config_schema = tasks.TransferTask

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
    def __init__(self, master, grid, task: tasks.TransferTask = None):
        super().__init__(master)

        self.grid(**grid)
        self.columnconfigure(0, weight=1)

        # COIN X
        self.coin_x_label = customtkinter.CTkLabel(
            self,
            text="Coin to transfer:",
        )
        self.coin_x_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 0))

        coin_x = getattr(task, "coin_x", self.coin_options[0])
        self.coin_x_combobox = customtkinter.CTkComboBox(
            self,
            values=self.coin_options,
            width=120,
        )
        self.coin_x_combobox.set(coin_x.upper())
        self.coin_x_combobox.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 0))

        # MIN AMOUNT OUT
        min_amount_out = getattr(task, "min_amount_out", "")
        self.min_amount_out_element = CTkEntryWithLabel(
            self,
            label_text="Min amount out:",
            width=120,
            textvariable=Variable(value=min_amount_out),
        )
        self.min_amount_out_element.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 0))

        # MAX AMOUNT OUT
        max_amount_out = getattr(task, "max_amount_out", "")
        self.max_amount_out_element = CTkEntryWithLabel(
            self,
            label_text="Max amount out:",
            width=120,
            textvariable=Variable(value=max_amount_out),
        )
        self.max_amount_out_element.grid(row=2, column=1, sticky="e", padx=20, pady=(10, 0))

        # USE ALL BALANCE CHECKBOX
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

        # SEND PERCENT BALANCE CHECKBOX
        self.send_percent_balance_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Send % of balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
        )
        if getattr(task, "send_percent_balance", False):
            self.send_percent_balance_checkbox.select()

        self.send_percent_balance_checkbox.grid(row=4, column=0, sticky="w", padx=20, pady=(10, 20))

        if getattr(task, "use_all_balance", False):
            self.use_all_balance_checkbox.select()
            self.min_amount_out_element.entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_out_element.entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(
                state="disabled"
            )

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





