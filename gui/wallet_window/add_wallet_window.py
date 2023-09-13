import tkinter
import tkinter.messagebox
from typing import Callable

import customtkinter
from loguru import logger
from pydantic import ValidationError

from gui import objects
from gui import constants
from src import enums
from src.schemas.wallet_data import WalletData
from utlis.key_manager.key_manager import get_argent_addr_from_private_key
from utlis.key_manager.key_manager import get_braavos_addr_from_private_key
import config


class AddWalletFrame(customtkinter.CTkFrame):
    def __init__(
        self, master, on_add_wallet: Callable[[WalletData], None] = None, **kwargs
    ):
        super().__init__(master, **kwargs)

        self.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)

        # NAME
        self.name_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Name",
        )
        self.name_entry.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        # PRIVATE KEY
        self.private_key_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Private key*",
        )
        self.private_key_entry.grid(row=1, column=0, padx=10, pady=0, sticky="w")
        self.private_key_entry.bind("<FocusOut>", self.private_key_changed)

        self.invalid_entry_label = customtkinter.CTkLabel(
            self.private_key_entry,
            text="",
            text_color=constants.ERROR_HEX,
        )
        self.invalid_entry_label.grid(row=1, column=1, padx=10, pady=0, sticky="w")

        # ADDRESS
        self.address_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Address",
            state="disabled"
        )
        self.address_entry.entry.configure(
            fg_color="gray25"
        )
        self.address_entry.grid(row=2, column=0, padx=10, pady=0, sticky="w")

        # PROXY
        self.proxy_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Proxy",
        )
        self.proxy_entry.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        # TYPE
        self.private_key_type_radio_var = tkinter.StringVar(
            value=enums.PrivateKeyType.argent.value
        )
        self.argent_radio_button = customtkinter.CTkRadioButton(
            self,
            text="Argent",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.argent.value,
            command=self.toggle_wallet_type,
        )
        self.argent_radio_button.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.braavos_radio_button = customtkinter.CTkRadioButton(
            self,
            text="Braavos",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.braavos.value,
            command=self.toggle_wallet_type,
        )
        self.braavos_radio_button.grid(row=4, column=0, padx=110, pady=10, sticky="w")

        self.add_button = customtkinter.CTkButton(
            self,
            text="Add",
            command=lambda: on_add_wallet(self.get_wallet_data()),
        )
        self.add_button.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        self.__last_private_key_repr = ""
        self.__private_key = ""

    @property
    def private_key_type(self):
        return enums.PrivateKeyType[self.private_key_type_radio_var.get()]

    def set_private_key_invalid_label(self):
        self.invalid_entry_label.configure(text="Invalid key")

    def set_private_key_valid_label(self):
        self.invalid_entry_label.configure(text="")

    def set_address(self, private_key: str):
        if self.private_key_type == enums.PrivateKeyType.braavos:
            address = hex(get_braavos_addr_from_private_key(private_key))
        elif self.private_key_type == enums.PrivateKeyType.argent:
            address = hex(get_argent_addr_from_private_key(private_key))
        else:
            self.set_private_key_invalid_label()
            logger.error("Invalid key type")
            return

        address_repr = f"{address[:6]}.....{address[-6:]}"
        self.address_entry.entry.configure(
            textvariable=tkinter.StringVar(value=address_repr)
        )

    def toggle_wallet_type(self):
        try:
            self.set_address(self.__private_key)
            self.set_private_key_valid_label()

        except ValueError as e:
            self.set_private_key_invalid_label()
            logger.error("Invalid key")
            logger.exception(e)
            return

    def private_key_changed(self, event):
        try:
            private_key = self.private_key_entry.get().strip()
            if not private_key:
                return

            if "....." in private_key:
                return

            elif len(private_key) != config.STARK_KEY_LENGTH:
                self.set_private_key_invalid_label()
                self.__last_private_key_repr = private_key
                logger.error("Invalid key")
                return

            if private_key[:6] != self.__private_key[:6]:
                self.__private_key = private_key

            self.set_address(private_key)
            self.set_private_key_valid_label()

            private_key_repr = f"{private_key[:6]}.....{private_key[-6:]}"
            self.private_key_entry.entry.configure(
                textvariable=tkinter.StringVar(value=private_key_repr)
            )
            self.__last_private_key_repr = private_key_repr

        except ValueError as e:
            self.set_private_key_invalid_label()
            logger.error("Invalid key")
            logger.exception(e)
            return

    def get_wallet_data(self) -> WalletData:
        try:
            private_key = self.private_key_entry.get().strip()
            if "....." in private_key:
                private_key = self.__private_key

            name = self.name_entry.get()
            proxy = self.proxy_entry.get()
            private_key_type = self.private_key_type

            wallet_data = WalletData(
                name=name,
                private_key=private_key,
                proxy=proxy,
                type=private_key_type,
            )

            return wallet_data

        except ValidationError as e:
            error_messages = e.errors()[0]["msg"]
            logger.error(error_messages)
            logger.exception(e)
            tkinter.messagebox.showerror(
                title="Config validation error", message=error_messages
            )


class AddWalletWindow(customtkinter.CTkToplevel):
    def __init__(self, master, on_add_wallet: Callable[[WalletData], None] = None):
        super().__init__(master)

        self.title("Add wallet")

        self.geometry("300x350")

        self.after(10, self.focus_force)

        self.grid_columnconfigure(0, weight=1, uniform="a")

        self.frame = AddWalletFrame(self, on_add_wallet=on_add_wallet)

    def close(self):
        self.frame.destroy()
        self.destroy()
