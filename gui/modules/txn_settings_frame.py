import customtkinter
from tkinter import Variable

from src.schemas.tasks.base.base import TaskBase


class TxnSettingFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task: TaskBase = None,
    ):
        super().__init__(master)

        self.frame = customtkinter.CTkFrame(master, width=100)
        self.frame.grid(**grid,)
        self.frame.grid_columnconfigure(0, weight=1)
        # self.frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # MAX FEE
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

        max_fee = getattr(task, "max_fee", "") if getattr(task, "forced_gas_limit", False) else ""
        state = "normal" if getattr(task, "forced_gas_limit", False) else "disabled"
        color = "#343638" if getattr(task, "forced_gas_limit", False) else "#3f3f3f"
        self.max_fee_entry = customtkinter.CTkEntry(
            self.frame,
            width=100,
            state=state,
            fg_color=color,
            textvariable=Variable(value=max_fee),
        )
        self.max_fee_entry.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w",
        )

        # FORCED MAX FEE CHECKBOX
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
        if getattr(task, "forced_gas_limit", False):
            self.forced_gas_limit_check_box.select()

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
