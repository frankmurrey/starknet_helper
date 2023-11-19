import tkinter.messagebox
from typing import TYPE_CHECKING, Union

import customtkinter
from PIL import Image

from src.schemas.tasks.base.swap import TaskBase
from src.paths import GUI_DIR
from src import enums
from gui import constants

if TYPE_CHECKING:
    from gui.wallet_right_window.actions_frame import CurrentActionsFrame


class WalletActionFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any,
            grid: dict,
            task: TaskBase,
            tab_name: str,
            repeats: int,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.master: 'CurrentActionsFrame' = master
        self.actions = self.master.master.actions

        self.task = task
        self.repeats = repeats
        self.tab_name = tab_name

        self.grid(**grid)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="uniform")
        self.grid_columnconfigure(4, weight=0)
        self.grid_rowconfigure((0, 1), weight=1)

        self.module_label = customtkinter.CTkLabel(
            self,
            text=task.module_name.title(),
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.module_label.grid(row=0, column=0, padx=(10, 0), pady=2, sticky="we")

        self.action_label = customtkinter.CTkLabel(
            self,
            text=task.module_type.title(),
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.action_label.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="we")

        self.action_info_label = customtkinter.CTkLabel(
            self,
            text=task.action_info,
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.action_info_label.grid(row=0, column=2, padx=(20, 0), pady=0, sticky="we")

        self.repeats_label = customtkinter.CTkLabel(
            self, text=str(repeats), font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.repeats_label.grid(row=0, column=3, padx=(40, 0), pady=2, sticky="we")

        edit_image = customtkinter.CTkImage(
            light_image=Image.open(f"{GUI_DIR}/images/edit_button.png"),
            dark_image=Image.open(f"{GUI_DIR}/images/edit_button.png"),
            size=(20, 20)
        )

        self.edit_button = customtkinter.CTkButton(
            self,
            text="",
            width=5,
            bg_color='transparent',
            fg_color='transparent',
            text_color='blue',
            image=edit_image,
            hover=False,
            command=self.edit_button_event
        )
        self.edit_button.grid(row=0, column=4, padx=(0, 35), pady=2, sticky="e")

        delete_image = customtkinter.CTkImage(
            light_image=Image.open(f"{GUI_DIR}/images/minus_button.png"),
            dark_image=Image.open(f"{GUI_DIR}/images/minus_button.png"),
            size=(12, 12)
        )

        self.delete_button = customtkinter.CTkButton(
            self,
            text="",
            width=5,
            bg_color='transparent',
            fg_color='transparent',
            text_color='red',
            image=delete_image,
            hover=False,
            command=self.delete_button_event
        )
        self.delete_button.grid(row=0, column=4, padx=(0, 10), pady=2, sticky="e")

    def set_task_active(self):
        try:
            self.task.task_status = enums.TaskStatus.PROCESSING
            self.configure(border_width=1, border_color=constants.ACTIVE_ACTION_HEX)
        except IndexError:
            pass

    def set_task_completed(self):
        try:
            self.task.task_status = enums.TaskStatus.SUCCESS
            self.configure(border_width=1, border_color=constants.SUCCESS_HEX)
        except IndexError:
            pass

    def set_task_failed(self):
        try:
            self.task.task_status = enums.TaskStatus.FAILED
            self.configure(border_width=1, border_color=constants.ERROR_HEX)
        except IndexError:
            pass

    def set_task_test_mode(self):
        try:
            self.configure(border_width=1, border_color=constants.TEST_MODE_GREY_HEX)
        except IndexError:
            pass

    def set_task_empty(self):
        try:
            self.configure(border_width=0)
        except Exception as ex:
            pass

    def delete_button_event(self):
        if self.master.master.is_running:
            tkinter.messagebox.showerror("Error", "You can't delete action while it's running")
            return

        try:
            action_frame = self.master.master
            actions = action_frame.actions
            for action in actions:
                if action['task_config'].task_id == self.task.task_id:
                    actions.remove(action)
                    break

            action_frame.redraw_current_actions_frame()
        except Exception as e:
            tkinter.messagebox.showerror("Error", f"Error while deleting action: {e}")

    def edit_task_callback(self, action: Union[dict, None]):
        if action is None:
            return

        self.master.master.edit_action(action)

    def edit_button_event(self):
        if self.master.master.is_running:
            tkinter.messagebox.showerror("Error", "You can't edit action while it's running")
            return

        action = {
            "task_config": self.task,
            "repeats": self.repeats,
            "tab_name": self.tab_name
        }
        self.master.master.button_actions_frame.edit_action_button_event(
            on_action_save=self.edit_task_callback,
            action=action
        )
