import customtkinter
from tkinter import Variable


class TxnSettingFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid
    ):
        super().__init__(master)

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(**grid)
        self.frame.grid_columnconfigure((0, 1), weight=1, uniform="a")
        self.frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.max_fee_label = customtkinter.CTkLabel(
            self.frame,
            text="Max fee (GWEI):"
        )
        self.max_fee_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )
        self.max_fee_entry = customtkinter.CTkEntry(
            self.frame,
            width=100,
            textvariable=Variable(value=150000)
        )
        self.max_fee_entry.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )

        self.forced_gas_limit_check_box = customtkinter.CTkCheckBox(
            self.frame,
            text="Forced Max fee",
            checkbox_height=18,
            checkbox_width=18,
            onvalue=True,
            offvalue=False
        )
        self.forced_gas_limit_check_box.grid(
            row=2,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )

        self.min_delay_sec_label = customtkinter.CTkLabel(
            self.frame,
            text="Min delay (sec):"
        )
        self.min_delay_sec_label.grid(
            row=3,
            column=0,
            padx=20,
            pady=0,
            sticky='w'
        )

        self.min_delay_sec_entry = customtkinter.CTkEntry(
            self.frame,
            width=100,
            textvariable=Variable(value=40)
        )
        self.min_delay_sec_entry.grid(
            row=4,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky='w'
        )

        self.max_delay_sec_label = customtkinter.CTkLabel(
            self.frame,
            text="Max delay (sec):"
        )
        self.max_delay_sec_label.grid(
            row=3,
            column=1,
            padx=20,
            pady=0,
            sticky='w'
        )

        self.max_delay_sec_entry = customtkinter.CTkEntry(
            self.frame,
            width=100,
            textvariable=Variable(value=80)
        )
        self.max_delay_sec_entry.grid(
            row=4,
            column=1,
            padx=20,
            pady=(0, 10),
            sticky='w'
        )

        self.txn_wait_timeout_sec_label = customtkinter.CTkLabel(
            self.frame,
            text="Txn wait time (sec):"
        )
        self.txn_wait_timeout_sec_label.grid(
            row=5,
            column=0,
            padx=20,
            pady=0,
            sticky='w'
        )

        self.txn_wait_timeout_sec_entry = customtkinter.CTkEntry(
            self.frame,
            state="disabled",
            fg_color='#3f3f3f',
            width=100
        )
        self.txn_wait_timeout_sec_entry.grid(
            row=6,
            column=0,
            padx=20,
            pady=(0, 5),
            sticky='w'
        )

        self.wait_for_receipt_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Wait for txn",
            checkbox_height=18,
            checkbox_width=18,
            onvalue=True,
            offvalue=False,
            command=self.wait_for_txn_checkbox_event
        )
        self.wait_for_receipt_checkbox.grid(
            row=7,
            column=0,
            padx=20,
            pady=10,
            sticky="w"
        )

    def wait_for_txn_checkbox_event(self):
        if self.wait_for_receipt_checkbox.get():
            self.txn_wait_timeout_sec_entry.configure(
                state="normal",
                textvariable=Variable(value=140),
                fg_color='#343638'
            )
        else:
            self.txn_wait_timeout_sec_entry.configure(
                state="disabled",
                textvariable=Variable(value=""),
                fg_color='#3f3f3f'
            )
