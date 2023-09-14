import tkinter

import customtkinter

from gui.main_window.interactions_top_level_window import FloatSpinbox
from src import enums


class ToolsWindow(customtkinter.CTkToplevel):
    def __init__(
            self,
            master,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title("Tools")
        self.title("New action")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.master = master

        self.wallet_generator_frame = WalletGeneratorFrame(master=self)


class WalletGeneratorFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            *args,
            **kwargs
    ):
        super().__init__(master=master, *args, **kwargs)
        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=0)

        self.label = customtkinter.CTkLabel(
            master=self,
            text="Generate wallets (mnemonic + key pair)",
            font=customtkinter.CTkFont(size=15, weight="bold")
        )
        self.label.grid(row=0, column=0, sticky="wn", pady=10, padx=10)

        self.amount_label = customtkinter.CTkLabel(
            master=self,
            text="Amount:",
            font=customtkinter.CTkFont(size=12)
        )
        self.amount_label.grid(row=1, column=0, sticky="w", pady=(0, 0), padx=10)

        self.amount_spinbox = FloatSpinbox(
            master=self,
            step_size=5,
            max_value=500,
            start_index=5,
        )
        self.amount_spinbox.grid(row=2, column=0, sticky="w", pady=(0, 10), padx=10)

        self.private_key_type_radio_var = tkinter.StringVar(
            value=enums.PrivateKeyType.argent.value
        )

        self.argent_type_radiobutton = customtkinter.CTkRadioButton(
            master=self,
            text="Argent",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.argent.value,
            font=customtkinter.CTkFont(size=12)
        )
        self.argent_type_radiobutton.grid(row=3, column=0, sticky="w", pady=10, padx=10)

        self.braavos_type_radiobutton = customtkinter.CTkRadioButton(
            master=self,
            text="Braavos",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.braavos.value,
            font=customtkinter.CTkFont(size=12)
        )
        self.braavos_type_radiobutton.grid(row=3, column=0, sticky="w", pady=10, padx=90)




