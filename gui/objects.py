import tkinter
from typing import Optional, Union, Tuple

import customtkinter


class CTkEntryWithLabel(customtkinter.CTkFrame):
    """
    Entry with a label
    """

    def __init__(
            self,
            master,
            label_text: str,

            textvariable: Union[tkinter.Variable, None] = None,

            width: int = 140,
            height: int = 28,

            state: str = tkinter.NORMAL,
            **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label = customtkinter.CTkLabel(
            self,
            text=label_text,
        )
        self.label.grid(row=0, column=0, padx=0, pady=0, sticky="w")

        self.entry = customtkinter.CTkEntry(
            self,
            state=state,
            textvariable=textvariable,
            width=width,
            height=height,
            **kwargs
        )
        self.entry.grid(row=1, column=0, padx=0, pady=0, sticky="w")

    def get(self):
        return self.entry.get()

    def bind(self, sequence, command, add=True):
        self.entry.bind(sequence, command, add)
