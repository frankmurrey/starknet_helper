import customtkinter

from src.schemas.configs.transaction_settings_base.swap import SwapSettingsBase


class WalletActionFrame(customtkinter.CTkFrame):
    def __init__(
        self, master: any, grid: dict, task: SwapTaskBase, repeats: int, **kwargs
    ):
        super().__init__(master, **kwargs)

        self.grid(**grid)
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="uniform")
        self.grid_rowconfigure((0, 1), weight=1)

        self.module_label = customtkinter.CTkLabel(
            self,
            text=task.module_name.title(),
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.module_label.grid(row=0, column=0, padx=(10, 0), pady=0)

        self.action_label = customtkinter.CTkLabel(
            self,
            text=task.module_type.title(),
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.action_label.grid(row=0, column=1, padx=(15, 0), pady=0)

        self.repeats_label = customtkinter.CTkLabel(
            self, text=str(repeats), font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.repeats_label.grid(row=0, column=2, padx=(0, 5), pady=0)
