import customtkinter
from tkinter import Variable


class TxnSettingFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid
    ):
        super().__init__(master)

        self.frame = customtkinter.CTkFrame(master, width=100)
        self.frame.grid(**grid,)
        self.frame.grid_columnconfigure(0, weight=1)
        # self.frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

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
            state="disabled",
            fg_color="#3f3f3f",
        )
        self.max_fee_entry.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w",
        )

        self.forced_gas_limit_check_box = customtkinter.CTkCheckBox(
            self.frame,
            text="Forced Max fee",
            checkbox_height=18,
            checkbox_width=18,
            onvalue=True,
            offvalue=False,
            command=self.forced_gas_limit_check_box_event,
        )
        self.forced_gas_limit_check_box.grid(
            row=2,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )

    def forced_gas_limit_check_box_event(self):
        if self.forced_gas_limit_check_box.get() is True:
            self.max_fee_entry.configure(
                state="normal",
                textvariable=Variable(value=250000),
                fg_color="#343638"
            )
        else:
            self.max_fee_entry.configure(
                state="disabled",
                textvariable=Variable(value=""),
                fg_color="#3f3f3f"
            )
