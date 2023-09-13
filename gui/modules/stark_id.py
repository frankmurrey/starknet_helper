from typing import Callable
from typing import Union
from tkinter import messagebox

import customtkinter

from tkinter import Variable
from loguru import logger

from gui.modules.txn_settings_frame import TxnSettingFrame


class StarkIdMintTab:
    def __init__(
            self,
            tabview,
            tab_name
    ):
        self.tabview = tabview

        self.tab_name = tab_name

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid={
                "row": 0,
                "column": 0,
                "padx": 20,
                "pady": 20,
                "sticky": "nsew"
            }
        )