from tkinter import messagebox
from typing import Callable, Union
from pydantic.error_wrappers import ValidationError

import customtkinter
from loguru import logger

from src import enums
from src.schemas import tasks
from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.objects import CTkCustomTextBox


class ZeriusTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.ZeriusMintTask = None
    ):
        self.tabview = tabview

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        mint_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.mint_frame = MintFrame(
            master=self.tabview.tab(tab_name),
            grid=mint_frame_grid,
            task=task
        )

        txn_settings_frame_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid=txn_settings_frame_grid,
            task=task
        )

    def build_config_data(self):
        config_schema = tasks.ZeriusMintTask
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            return config_schema(
                max_fee=self.txn_settings_frame.max_fee_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
                use_reff=self.mint_frame.use_reff_checkbox.get()
            )

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class MintFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task=None
    ):
        super().__init__(master)

        self.grid(**grid)
        self.grid_columnconfigure((0), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        check_box_value = getattr(task, "use_reff", True)
        self.use_reff_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Use creator refferal (thanks <3)",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18
        )
        self.use_reff_checkbox.select()
        if not check_box_value:
            self.use_reff_checkbox.deselect()

        self.use_reff_checkbox.grid(row=0, column=0, sticky="w", padx=20, pady=20)
