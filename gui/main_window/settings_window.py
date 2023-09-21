import tkinter
from tkinter import messagebox

import customtkinter

from src import exceptions
from src.storage import Storage
from src import paths
from src.schemas.app_config import AppConfigSchema
from utils.file_manager import FileManager
from gui.modules.frames import FloatSpinbox
from utils.gas_price import get_eth_mainnet_gas_price
from gui import constants


class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Settings")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.master = master

        self.app_config_frame = AppConfigFrame(master=self)


class AppConfigFrame(customtkinter.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=0)

        self.app_config: AppConfigSchema = Storage().app_config

        self.label = customtkinter.CTkLabel(
            master=self,
            text="App config:",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        )
        self.label.grid(row=0, column=0, sticky="wn", pady=10, padx=15)

        is_preserve_on = self.app_config.preserve_logs
        self.preserve_logs_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Preserve logs",
            variable=tkinter.Variable(value=is_preserve_on),
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            text_color="#6fc276" if is_preserve_on else "#F47174",
            onvalue=True,
            offvalue=False,
            command=self.preserve_logs_checkbox_event
        )
        self.preserve_logs_checkbox.grid(row=1, column=0, sticky="wn", pady=10, padx=15)

        self.stark_rpc_url_label = customtkinter.CTkLabel(
            master=self, text="StarkNet RPC URL:", font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.stark_rpc_url_label.grid(row=2, column=0, sticky="w", pady=(5, 0), padx=15)

        self.stark_rpc_url_entry = customtkinter.CTkEntry(
            master=self,
            width=280,
            font=customtkinter.CTkFont(size=12),
            textvariable=tkinter.StringVar(value=self.app_config.rpc_url),
        )
        self.stark_rpc_url_entry.grid(row=3, column=0, sticky="w", pady=(0, 15), padx=15)

        self.eth_mainnet_rpc_url_label = customtkinter.CTkLabel(
            master=self, text="ETH Mainnet RPC URL:", font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.eth_mainnet_rpc_url_label.grid(row=4, column=0, sticky="w", pady=(5, 0), padx=15)

        self.eth_mainnet_rpc_url_entry = customtkinter.CTkEntry(
            master=self,
            width=280,
            font=customtkinter.CTkFont(size=12),
            textvariable=tkinter.StringVar(value=self.app_config.eth_mainnet_rpc_url),
        )
        self.eth_mainnet_rpc_url_entry.grid(row=5, column=0, sticky="w", pady=(0, 10), padx=15)

        self.target_eth_mainnet_gas_price_label = customtkinter.CTkLabel(
            master=self, text="Target ETH Mainnet Gas Price (Gwei):", font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.target_eth_mainnet_gas_price_label.grid(row=6, column=0, sticky="w", pady=(5, 0), padx=15)

        self.target_eth_gas_price_spinbox = FloatSpinbox(
            master=self,
            step_size=1,
            width=110
        )
        self.target_eth_gas_price_spinbox.entry.configure(
            textvariable=tkinter.Variable(value=self.app_config.target_eth_mainnet_gas_price)
        )
        self.target_eth_gas_price_spinbox.grid(row=7, column=0, sticky="w", pady=(0, 10), padx=15)

        self.current_gas_price_button = customtkinter.CTkButton(
            master=self,
            text="Get current gas price",
            text_color="gray70",
            fg_color='transparent',
            hover=False,
            font=customtkinter.CTkFont(size=12, underline=True, weight="bold"),
            command=self.current_gas_price_button_event
        )
        self.current_gas_price_button.grid(row=7, column=0, sticky="w", pady=(0, 10), padx=(140, 15))

        self.max_time_to_wait_target_gas_price_label = customtkinter.CTkLabel(
            master=self, text="Time to wait target gas price (sec):", font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.max_time_to_wait_target_gas_price_label.grid(row=8, column=0, sticky="w", pady=(5, 0), padx=15)

        self.max_time_to_wait_target_gas_price_spinbox = FloatSpinbox(
            master=self,
            step_size=5,
            start_index=self.app_config.time_to_wait_target_gas_price_sec,
            width=110
        )
        self.max_time_to_wait_target_gas_price_spinbox.grid(row=9, column=0, sticky="w", pady=(0, 20), padx=15)

        self.save_button = customtkinter.CTkButton(
            master=self,
            text="Save",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            command=self.save_button_event
        )
        self.save_button.grid(row=10, column=0, sticky="w", pady=15, padx=15)

    def preserve_logs_checkbox_event(self):
        if self.preserve_logs_checkbox.get():
            self.preserve_logs_checkbox.configure(
                text_color="#6fc276"
            )
        else:
            self.preserve_logs_checkbox.configure(
                text_color="#F47174"
            )

    def current_gas_price_button_event(self):
        rpc_url = self.eth_mainnet_rpc_url_entry.get()
        if not rpc_url:
            messagebox.showerror("Error", "Please enter ETH Mainnet RPC URL")
            return

        current_gas_price = get_eth_mainnet_gas_price(rpc_url=self.app_config.eth_mainnet_rpc_url)
        if current_gas_price is None:
            messagebox.showerror("Error", "Can't get current gas price")
            return

        if int(current_gas_price) <= 20:
            color = constants.SUCCESS_HEX

        elif int(current_gas_price) > 20:
            color = constants.WARNING_HEX

        elif int(current_gas_price) > 50:
            color = constants.ERROR_HEX

        else:
            color = constants.ERROR_HEX

        self.current_gas_price_button.configure(text=f"Gas price: {round(current_gas_price, 2)} Gwei",
                                                text_color=color)

    def save_button_event(self):
        try:
            app_config = AppConfigSchema(
                preserve_logs=self.preserve_logs_checkbox.get(),
                rpc_url=self.stark_rpc_url_entry.get(),
                eth_mainnet_rpc_url=self.eth_mainnet_rpc_url_entry.get(),
                target_eth_mainnet_gas_price=self.target_eth_gas_price_spinbox.get(),
                time_to_wait_target_gas_price_sec=self.max_time_to_wait_target_gas_price_spinbox.get()
            )
            Storage().update_app_config(app_config)
            try:
                FileManager.write_data_to_json_file(
                    file_path=paths.APP_CONFIG_FILE,
                    data=app_config.dict(),
                    raise_exception=True
                )
                messagebox.showinfo(
                    title="Success",
                    message="App config saved successfully"
                )

            except exceptions.AppValidationError as e:
                messagebox.showerror(
                    title="Config validation error", message=e.message
                )
                return None

        except exceptions.ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None

