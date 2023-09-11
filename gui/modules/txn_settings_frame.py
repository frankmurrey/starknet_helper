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
