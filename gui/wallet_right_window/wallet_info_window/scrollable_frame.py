import asyncio
import tkinter
import tkinter.messagebox
from typing import Callable, Union, List
from threading import Thread

import customtkinter

from src import enums
from gui.wallet_right_window.wallet_info_window.info_table_top import WalletInfoTopFrame


class WalletInfoScrollableFrame(customtkinter.CTkScrollableFrame):
    def __init__(
            self,
            master,
            grid,
            **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.grid(**grid)

        self.items: List[WalletInfoTopFrame] = []

    def set_item(self, item: WalletInfoTopFrame):
        self.items.append(item)
        self.redraw_frame()

    def redraw_frame(self):
        for item in self.items:
            item.grid_forget()
            item.destroy()

        if not self.items:
            return

        start_row = 0
        start_column = 0

        for item_index, item in enumerate(self.items):
            item.grid(
                row=start_row + item_index + 1,
                column=start_column,
                sticky="ew",
                pady=3
            )


class WalletInfoWindow(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Wallet Info")
        self.geometry("500x600")

        self.after(10, self.focus_force)

        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.top_frame = WalletInfoTopFrame(
            self,
            grid={
                "row": 0,
                "column": 0,
                "sticky": "ew",
                "padx": 10,
                "pady": 10,
            }
        )

        self.frame = WalletInfoScrollableFrame(
            self,
            grid={
                "row": 1,
                "column": 0,
                "sticky": "nsew",
                "padx": 10,
                "pady": 10,
            }
        )

    def close(self):
        self.frame.destroy()
        self.destroy()
