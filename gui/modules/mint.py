from tkinter import Variable, messagebox
from typing import Callable, Union

import customtkinter
from loguru import logger
from pydantic.error_wrappers import ValidationError

from src.schemas import tasks
from src import enums
from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.objects import CTkCustomTextBox


MINT_TASKS = {
    enums.ModuleName.IDENTITY: tasks.IdentityMintTask,
    enums.ModuleName.STARK_VERSE: tasks.StarkVersePublicMintTask,
}


class MintTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.IdentityMintTask = None

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
            task=task,
        )

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid={
                "row": 1,
                "column": 0,
                "padx": 20,
                "pady": 20,
                "sticky": "nsew"
            },
            task=task,
        )

        text_box_grid = {
            "row": 2,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "ew"
        }

        text = f"- StarkID mint's with random unused ID.\n\n"

        self.info_textbox = CTkCustomTextBox(
            master=self.tabview.tab(tab_name),
            grid=text_box_grid,
            text=text,
        )

    def get_config_schema(self) -> Union[Callable, None]:
        protocol = self.mint_frame.protocol_combobox.get().lower()
        return MINT_TASKS.get(protocol, None)

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            return config_schema(
                max_fee=self.txn_settings_frame.max_fee_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
            )

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class MintFrame(customtkinter.CTkFrame):
    def __init__(self, master, grid, task=None):
        super().__init__(master)

        self.grid(**grid)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # PROTOCOL
        self.protocol_label = customtkinter.CTkLabel(
            master=self,
            text="Protocol:"
        )
        self.protocol_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        protocol = getattr(task, "module_name", self.protocol_options[0])
        self.protocol_combobox = customtkinter.CTkComboBox(
            master=self,
            values=self.protocol_options,
            width=120,
        )
        self.protocol_combobox.set(protocol.upper())
        self.protocol_combobox.grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 20)
        )

    @property
    def protocol_options(self):
        return [
            enums.ModuleName.IDENTITY.upper(),
            enums.ModuleName.STARK_VERSE.upper(),
        ]







