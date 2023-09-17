import customtkinter

from src.schemas.tasks.base.swap import TaskBase


class WalletActionFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any,
            grid: dict,
            task: TaskBase,
            repeats: int,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.grid(**grid)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="uniform")
        self.grid_rowconfigure((0, 1), weight=1)

        self.module_label = customtkinter.CTkLabel(
            self,
            text=task.module_name.title(),
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.module_label.grid(row=0, column=0, padx=(1, 15), pady=0, sticky="ew")

        self.action_label = customtkinter.CTkLabel(
            self,
            text=task.module_type.title(),
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.action_label.grid(row=0, column=1, padx=(0, 0), pady=0, sticky="ew")

        self.repeats_label = customtkinter.CTkLabel(
            self, text=str(repeats), font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.repeats_label.grid(row=0, column=2, padx=(15, 0), pady=0, sticky="ew")

        self.action_info_label = customtkinter.CTkLabel(
            self,
            text=task.action_info,
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.action_info_label.grid(row=0, column=3, padx=(0, 0), pady=0)
