import tkinter
import tkinter.messagebox
from typing import Callable, Union

import customtkinter
from pydantic import ValidationError

from src import enums
from src.schemas.wallet_data import WalletData
from src.schemas.proxy_data import ProxyData

from gui import objects
from gui.wallet_right_window.wallet_window.empty_wallet_data import EmptyUiWalletData
from gui.wallet_right_window.wallet_window.private_key_entry import PrivateKeyEntry
from gui.wallet_right_window.wallet_window.address_entry import AddressEntry
from gui.wallet_right_window.wallet_window.pair_address_entry import PairAddressEntry


class WalletFrame(customtkinter.CTkFrame):

    def __init__(
            self,
            master,
            on_wallet_save: Callable[[Union[WalletData, None]], None],
            wallet_data: WalletData = None,
            **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.wallet_data = wallet_data
        if self.wallet_data is None:
            self.wallet_data = EmptyUiWalletData()

        self.on_wallet_save = on_wallet_save

        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(6, weight=1)

        # NAME
        self.name_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Name",
            textvariable=tkinter.StringVar(value=self.wallet_data.name),
            width=200,
        )
        self.name_entry.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        # PRIVATE KEY
        self.private_key_entry = PrivateKeyEntry(
            self,
            private_key=self.wallet_data.private_key,
        )
        self.private_key_entry.grid(row=1, column=0, padx=10, pady=0, sticky="w")

        # ADDRESS
        self.address_entry = AddressEntry(
            self,
            address=self.wallet_data.address,
        )
        self.address_entry.grid(row=2, column=0, padx=10, pady=0, sticky="w")
        self.private_key_entry.set_focus_in_callback(self.address_entry.show_full_text)
        self.private_key_entry.set_focus_out_callback(self.address_entry.hide_full_text)
        self.private_key_entry.set_text_changed_callback(
            lambda: self.address_entry.set_address(
                self.private_key_entry.private_key,
                self.private_key_type,
                self.cairo_version,
            )
        )

        # PAIR ADDRESS
        self.pair_address_entry = PairAddressEntry(
            self,
            pair_address=self.wallet_data.pair_address,
        )
        self.pair_address_entry.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        # PROXY
        self.proxy_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Proxy",
            textvariable=tkinter.StringVar(
                value=self.wallet_data.proxy.to_string() if isinstance(self.wallet_data.proxy, ProxyData) else ""
            ),
            width=200,
        )
        self.proxy_entry.grid(row=4, column=0, padx=10, pady=0, sticky="w")

        # PRIVATE KEY TYPE
        self.private_key_type_radio_var = tkinter.StringVar(
            value=self.wallet_data.type.value
        )

        self.argent_radio_button = customtkinter.CTkRadioButton(
            self,
            text="Argent",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.argent.value,
            command=self.toggle_wallet_type,
        )
        self.argent_radio_button.grid(row=5, column=0, padx=10, pady=(20, 10), sticky="w")

        self.braavos_radio_button = customtkinter.CTkRadioButton(
            self,
            text="Braavos",
            variable=self.private_key_type_radio_var,
            value=enums.PrivateKeyType.braavos.value,
            command=self.toggle_wallet_type,
        )
        self.braavos_radio_button.grid(row=5, column=0, padx=110, pady=(20, 10), sticky="w")

        # CAIRO VERSION
        self.cairo_version_radio_var = tkinter.IntVar(value=self.wallet_data.cairo_version)

        self.cairo_version_radio_button_0 = customtkinter.CTkRadioButton(
            self,
            text="Cairo 0",
            variable=self.cairo_version_radio_var,
            value=0,
            command=self.toggle_cairo_version,
        )
        self.cairo_version_radio_button_0.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        self.cairo_version_radio_button_1 = customtkinter.CTkRadioButton(
            self,
            text="Cairo 1",
            variable=self.cairo_version_radio_var,
            value=1,
            command=self.toggle_cairo_version,
        )
        self.cairo_version_radio_button_1.grid(row=6, column=0, padx=110, pady=10, sticky="w")

        # ADD BUTTON
        self.add_button = customtkinter.CTkButton(
            self,
            text="Save",
            command=self.save_wallet_button_clicked,
        )
        self.add_button.grid(row=7, column=0, padx=10, pady=10, sticky="ws")

        self.__last_private_key_repr = ""
        self.__private_key = ""

    @property
    def private_key_type(self):
        return enums.PrivateKeyType[self.private_key_type_radio_var.get().strip()]

    @property
    def cairo_version(self):
        return self.cairo_version_radio_var.get()

    def toggle_wallet_type(self):
        try:
            self.address_entry.set_address(
                self.private_key_entry.private_key,
                self.private_key_type,
                self.cairo_version
            )
            self.private_key_entry.disable_invalid_warning()

        except ValueError as e:
            self.private_key_entry.enable_invalid_warning()
            return

    def toggle_cairo_version(self):
        try:
            self.address_entry.set_address(
                self.private_key_entry.private_key,
                self.private_key_type,
                self.cairo_version
            )
            self.private_key_entry.disable_invalid_warning()

        except ValueError as e:
            self.private_key_entry.enable_invalid_warning()
            return

    def get_wallet_data(self) -> WalletData:

        name = self.name_entry.get().strip()

        private_key = self.private_key_entry.private_key
        pair_address = self.pair_address_entry.pair_address

        proxy = self.proxy_entry.get().strip()
        private_key_type = self.private_key_type
        cairo_version = self.cairo_version

        wallet_data = WalletData(
            name=name,
            private_key=private_key,
            pair_address=pair_address,
            proxy=proxy,
            type=private_key_type,
            cairo_version=cairo_version,
        )

        return wallet_data

    def save_wallet_button_clicked(self):
        wallet_data = None

        try:
            wallet_data = self.get_wallet_data()
        except ValidationError as e:
            error_messages = e.errors()[0]["msg"]
            tkinter.messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            self.focus_force()

        self.on_wallet_save(wallet_data)


class WalletWindow(customtkinter.CTkToplevel):
    def __init__(
            self,
            master,
            wallet_data: WalletData = None,
            on_wallet_save: Callable[[WalletData], None] = None
    ):
        super().__init__(master)

        self.title("Add wallet")
        self.geometry("320x450")

        self.after(10, self.focus_force)

        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame = WalletFrame(
            self,
            on_wallet_save=on_wallet_save,
            wallet_data=wallet_data
        )

    def close(self):
        self.frame.destroy()
        self.destroy()
