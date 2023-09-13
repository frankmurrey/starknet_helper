import tkinter.messagebox
from tkinter import Variable
from typing import List

from gui.main_window.interactions_top_level_window import InteractionTopLevelWindow
from gui.main_window.wallet_action_frame import WalletActionFrame
from gui.modules.frames import FloatSpinbox

import customtkinter


class ActionsFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any,
            **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure((0, 1, 3, 4), weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.actions: List[dict] = []
        self.action_items: List[WalletActionFrame] = []

        self.table_top_frame = TableTopFrame(master=self)
        self.current_actions_frame = CurrentActionsFrame(master=self)
        self.button_actions_frame = ButtonActionsFrame(parent=self)

        self.run_settings_label = customtkinter.CTkLabel(
            self,
            text="Run settings:",
            font=customtkinter.CTkFont(size=18, weight="bold")
        )
        self.run_settings_label.grid(
            row=0,
            column=1,
            padx=20,
            pady=(10, 0),
            sticky="ws"
        )
        self.run_settings_frame = RunSettingsFrame(parent=self)

        self.start_button = customtkinter.CTkButton(
            self,
            text="Start",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=110,
            height=30
        )
        self.start_button.grid(
            row=4,
            column=0,
            padx=20,
            pady=10,
            sticky="w"
        )

    def set_action(
            self,
            action: dict
    ):
        if action is None:
            return

        self.actions.append(action)
        self.redraw_current_actions_frame()

    def redraw_current_actions_frame(self):
        if not self.actions:
            self.current_actions_frame.no_actions_label.grid(
                row=0,
                column=0,
                padx=40,
                pady=10
            )
        else:
            try:
                self.current_actions_frame.no_actions_label.grid_forget()
            except AttributeError:
                pass

        start_row = -1
        start_column = 0

        for action_index, action_data in enumerate(self.actions, start=1):
            actions_item_grid = {
                "row": start_row + action_index,
                "column": start_column,
                "padx": 5,
                "pady": 5,
                "sticky": "ew"
            }

            action_item = WalletActionFrame(
                master=self.current_actions_frame,
                grid=actions_item_grid,
                repeats=action_data["repeats"],
                fg_color="grey21",
                task=action_data["task"],
            )
            self.action_items.append(action_item)

    def remove_all_actions(self):
        if not self.actions:
            return

        msg_box = tkinter.messagebox.askyesno(
            title="Remove all",
            message="Are you sure you want to clear all actions?",
            icon="warning"
        )

        if not msg_box:
            return

        for action_index, action_item in enumerate(self.action_items):
            action_item.grid_forget()
            action_item.destroy()

        self.actions = []
        self.action_items = []
        self.redraw_current_actions_frame()


class TableTopFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any,
            **kwargs):
        super().__init__(master, **kwargs)

        self.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 0),
            sticky="nsew"
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="uniform")

        self.action_name_label = customtkinter.CTkLabel(
            self,
            text="Module",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.action_name_label.grid(
            row=0,
            column=0,
            padx=40,
            pady=0
        )

        self.action_type_label = customtkinter.CTkLabel(
            self,
            text="Action",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        self.action_type_label.grid(
            row=0,
            column=1,
            padx=40,
            pady=0
        )

        self.repeats_label = customtkinter.CTkLabel(
            self,
            text="Repeats",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.repeats_label.grid(
            row=0,
            column=2,
            padx=40,
            pady=0
        )


class CurrentActionsFrame(customtkinter.CTkScrollableFrame):
    def __init__(
            self,
            master: any,
            **kwargs):
        super().__init__(master, **kwargs)

        self.grid(
            row=1,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky="nsew"
        )
        self.grid_columnconfigure(0, weight=1)

        self.no_actions_label = customtkinter.CTkLabel(
            self,
            text="No actions",
            font=customtkinter.CTkFont(size=15, weight="bold")
        )
        self.no_actions_label.grid(
            row=0,
            column=0,
            padx=40,
            pady=10
        )


class ButtonActionsFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            parent: any,
            **kwargs):
        super().__init__(master=parent, **kwargs)
        self.parent = parent
        self.actions_top_level_window = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 1, 2, 4), weight=0)

        self.grid(
            row=2,
            column=0,
            padx=20,
            pady=(5, 20),
            sticky="nsew"
        )

        self.add_action_button = customtkinter.CTkButton(
            self,
            text="+",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=25,
            height=25,
            command=self.add_action_button_event
        )
        self.add_action_button.grid(
            row=0,
            column=0,
            padx=(30, 0),
            pady=(10, 10),
            sticky="wn"
        )

        self.add_action_label = customtkinter.CTkLabel(
            self,
            text="Add action",
            font=customtkinter.CTkFont(size=13, weight="bold")
        )
        self.add_action_label.grid(
            row=0,
            column=1,
            padx=(6, 0),
            pady=(10, 10),
            sticky="wn"
        )

        self.remove_all_actions_button = customtkinter.CTkButton(
            self,
            text="-",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            fg_color="#db524b",
            hover_color="#5e1914",
            width=25,
            height=25,
            command=self.parent.remove_all_actions
        )
        self.remove_all_actions_button.grid(
            row=0,
            column=2,
            padx=(20, 0),
            pady=(10, 10),
            sticky="ew"
        )

        self.remove_all_actions_label = customtkinter.CTkLabel(
            self,
            text="Clear all",
            font=customtkinter.CTkFont(size=13, weight="bold")
        )
        self.remove_all_actions_label.grid(
            row=0,
            column=3,
            padx=(6, 0),
            pady=(10, 10),
            sticky="w"
        )

        self.randomize_actions_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Randomize",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
        )
        self.randomize_actions_checkbox.grid(
            row=0,
            column=4,
            padx=(20, 0),
            pady=(10, 10),
            sticky="ew"
        )

    def add_action_button_event(self):
        if self.actions_top_level_window is None or not self.actions_top_level_window.winfo_exists():
            self.actions_top_level_window = InteractionTopLevelWindow(parent=self.master)
            self.actions_top_level_window.geometry("450x1000+1385+100")
            self.actions_top_level_window.resizable(False, False)
        else:
            self.actions_top_level_window.focus()


class RunSettingsFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            parent: any,
            **kwargs):
        super().__init__(master=parent, **kwargs)
        self.parent = parent

        self.grid(
            row=1,
            column=1,
            padx=20,
            pady=(10, 20),
            sticky="nsew",
            rowspan=2
        )

        self.grid_columnconfigure((0, 1), weight=1)

        self.test_mode_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Test mode",
            text_color="#F47174",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            command=self.test_mode_checkbox_event
        )
        self.test_mode_checkbox.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="ew"
        )

        self.min_delay_label = customtkinter.CTkLabel(
            self,
            text="Min delay (sec):",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.min_delay_label.grid(
            row=1,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.min_delay_entry_spinbox = FloatSpinbox(self,
                                                    step_size=5,
                                                    width=105)
        self.min_delay_entry_spinbox.entry.configure(
            textvariable=Variable(value=40)
        )
        self.min_delay_entry_spinbox.grid(
            row=2,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )

        self.max_delay_label = customtkinter.CTkLabel(
            self,
            text="Max delay (sec):",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.max_delay_label.grid(
            row=1,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.max_delay_entry_spinbox = FloatSpinbox(self,
                                                    step_size=5,
                                                    width=105)
        self.max_delay_entry_spinbox.entry.configure(
            textvariable=Variable(value=80)
        )
        self.max_delay_entry_spinbox.grid(
            row=2,
            column=1,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )

        txn_wait_timeout_seconds_label = customtkinter.CTkLabel(
            self,
            text="Wait timeout (sec):",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        txn_wait_timeout_seconds_label.grid(
            row=3,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.txn_wait_timeout_seconds_spinbox = FloatSpinbox(self,
                                                             step_size=5,
                                                             width=105)
        self.txn_wait_timeout_seconds_spinbox.entry.configure(
            state="disabled",
            fg_color="#3f3f3f",
            textvariable=Variable(value="")
        )
        self.txn_wait_timeout_seconds_spinbox.add_button.configure(
            state="disabled"
        )
        self.txn_wait_timeout_seconds_spinbox.subtract_button.configure(
            state="disabled"
        )
        self.txn_wait_timeout_seconds_spinbox.grid(
            row=4,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.wait_for_receipt_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Wait for txn",
            font=customtkinter.CTkFont(size=12),
            checkbox_width=18,
            checkbox_height=18,
            command=self.wait_for_txn_checkbox_event
        )
        self.wait_for_receipt_checkbox.grid(
            row=5,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky="w"
        )

    def wait_for_txn_checkbox_event(self):
        if self.wait_for_receipt_checkbox.get():
            self.txn_wait_timeout_seconds_spinbox.entry.configure(
                state="normal",
                fg_color="gray16",
                textvariable=Variable(value=120)
            )
            self.txn_wait_timeout_seconds_spinbox.add_button.configure(
                state="normal")

            self.txn_wait_timeout_seconds_spinbox.subtract_button.configure(
                state="normal")
        else:
            self.txn_wait_timeout_seconds_spinbox.entry.configure(
                state="disabled",
                fg_color="#3f3f3f",
                textvariable=Variable(value="")
            )
            self.txn_wait_timeout_seconds_spinbox.add_button.configure(
                state="disabled")

            self.txn_wait_timeout_seconds_spinbox.subtract_button.configure(
                state="disabled")

    def test_mode_checkbox_event(self):
        if self.test_mode_checkbox.get():
            self.test_mode_checkbox.configure(
                text_color="#6fc276"
            )
        else:
            self.test_mode_checkbox.configure(
                text_color="#F47174"
            )