import tkinter
from tkinter import filedialog
from tkinter import messagebox
from typing import Callable

import customtkinter
from loguru import logger

import config
from gui.main_window.interactions_top_level_window import FloatSpinbox
from utils.key_manager.generator.generator import Generator
from utils.xlsx import write_generated_wallets_to_xlsx

from src import enums


class ToolsWindow(customtkinter.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Tools")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.master = master

        self.wallet_generator_frame = WalletGeneratorFrame(master=self)
        self.key_extractor_frame = KeyExtractorFrame(master=self)


class WalletGeneratorFrame(customtkinter.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=0)

        self.label = customtkinter.CTkLabel(
            master=self,
            text="Generate wallets (mnemonic + key pair)",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        )
        self.label.grid(row=0, column=0, sticky="wn", pady=10, padx=15)

        self.amount_label = customtkinter.CTkLabel(
            master=self, text="Amount:", font=customtkinter.CTkFont(size=12)
        )
        self.amount_label.grid(row=1, column=0, sticky="w", pady=(0, 0), padx=15)

        self.amount_spinbox = FloatSpinbox(
            master=self,
            step_size=5,
            max_value=500,
            start_index=5,
        )
        self.amount_spinbox.grid(row=2, column=0, sticky="w", pady=(0, 10), padx=15)

        self.private_key_type_radio_var = tkinter.StringVar(
            value=enums.PrivateKeyType.argent.value
        )

        self.argent_type_radiobutton = customtkinter.CTkRadioButton(
            master=self,
            text="Argent",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.argent.value,
            font=customtkinter.CTkFont(size=12),
        )
        self.argent_type_radiobutton.grid(row=3, column=0, sticky="wsn", pady=(10, 10), padx=15)

        self.braavos_type_radiobutton = customtkinter.CTkRadioButton(
            master=self,
            text="Braavos",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.braavos.value,
            font=customtkinter.CTkFont(size=12),
        )
        self.braavos_type_radiobutton.grid(
            row=3, column=0, sticky="wsn", pady=(10, 10), padx=(100, 0)
        )

        self.generate_button = customtkinter.CTkButton(
            master=self,
            text="Save to file",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            command=self.generate_button_event,
        )
        self.generate_button.grid(row=4, column=0, sticky="w", pady=15, padx=15)

    def generate_button_event(self):
        amount = int(self.amount_spinbox.get())
        private_key_type = enums.PrivateKeyType(self.private_key_type_radio_var.get())

        wallets = Generator.generate_mnemonics_with_key_pair(
            amount=amount,
            wallet_type=private_key_type
        )

        file_path = filedialog.asksaveasfilename(
            title="Save wallets",
            defaultextension=".xlsx",
            filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"),),
            initialfile=f"generated_{private_key_type}.xlsx"
        )

        write_generated_wallets_to_xlsx(data=wallets, path=file_path)


class KeyExtractorFrame(customtkinter.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=0)

        self.uploaded_mnemonics: list = []

        self.label = customtkinter.CTkLabel(
            master=self,
            text="Convert mnemonics to private keys:",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        )
        self.label.grid(row=0, column=0, sticky="wn", pady=(10, 15), padx=15)

        self.upload_button = customtkinter.CTkButton(
            master=self,
            width=25,
            height=25,
            text="+",
            font=customtkinter.CTkFont(size=12),
            command=self.upload_button_event
        )
        self.upload_button.grid(row=1, column=0, sticky="w", pady=(0, 10), padx=15)

        self.uploaded_mnemonics_amount_label = customtkinter.CTkLabel(
            master=self, text="Uploaded: -", font=customtkinter.CTkFont(size=14, weight="bold")
        )
        self.uploaded_mnemonics_amount_label.grid(row=1, column=0, sticky="w", pady=(0, 10), padx=(50, 0))

        self.private_key_type_radio_var = tkinter.StringVar(
            value=enums.PrivateKeyType.argent.value
        )

        self.argent_type_radiobutton = customtkinter.CTkRadioButton(
            master=self,
            text="Argent",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.argent.value,
            font=customtkinter.CTkFont(size=12),
        )

        self.argent_type_radiobutton.grid(row=2, column=0, sticky="wsn", pady=(10, 10), padx=15)

        self.braavos_type_radiobutton = customtkinter.CTkRadioButton(
            master=self,
            text="Braavos",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.braavos.value,
            font=customtkinter.CTkFont(size=12),
        )

        self.braavos_type_radiobutton.grid(
            row=2, column=0, sticky="wsn", pady=(10, 10), padx=(100, 0)
        )

        self.extract_button = customtkinter.CTkButton(
            master=self,
            text="Save to file",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            command=self.extract_button_event,
        )

        self.extract_button.grid(row=4, column=0, sticky="w", pady=15, padx=15)

    def upload_button_event(self):
        file_path = filedialog.askopenfilename(title="Open file",
                                               filetypes=(("Text files", "*.txt"),))
        if not file_path:
            return

        try:
            with open(file_path, "r") as file:
                mnemonics_raw = file.read().splitlines()

                for mnemonic in mnemonics_raw:
                    if len(mnemonic.split(" ")) == config.MNEMONIC_LENGTH:
                        self.uploaded_mnemonics.append(mnemonic)

                self.uploaded_mnemonics_amount_label.configure(text=f"Uploaded: {len(self.uploaded_mnemonics)}")
                messagebox.showinfo(title="Info",
                                    message=f"Uploaded {len(self.uploaded_mnemonics)} mnemonics")

        except Exception as e:
            logger.error(f"Error while reading file: {e}")

    def extract_button_event(self):
        private_key_type = enums.PrivateKeyType(self.private_key_type_radio_var.get())

        if not self.uploaded_mnemonics:
            messagebox.showerror(title="Error",
                                 message="No mnemonics uploaded")
            return

        if private_key_type == enums.PrivateKeyType.argent.value:
            private_keys = Generator.extract_argent_keys_from_mnemonics(
                mnemonics=self.uploaded_mnemonics
            )
        else:
            private_keys = Generator.extract_braavos_keys_from_mnemonics(
                mnemonics=self.uploaded_mnemonics
            )

        file_path = filedialog.asksaveasfilename(title="Save keys",
                                                 defaultextension=".txt",
                                                 filetypes=(("Text files", "*.txt"),),
                                                 initialfile=f"extracted.txt")
        if not file_path:
            return

        with open(file_path, "w") as file:
            for private_key in private_keys:
                file.write(f"{private_key}\n")

            messagebox.showinfo(title="Info",
                                message=f"Extracted {len(private_keys)} keys")

