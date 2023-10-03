import tkinter
import tkinter.messagebox

import config
from src import enums
from gui import objects
from utils.key_manager.key_manager import get_braavos_addr_from_private_key, get_argent_addr_from_private_key


class AddressEntry(objects.CTkEntryWithLabel):
    def __init__(
            self,
            master,
            address: str,
            **kwargs
    ):
        super().__init__(
            master,
            label_text="Address",
            textvariable=tkinter.StringVar(value=address),
            width=200,
            state=tkinter.DISABLED,

            hide_on_focus_out=True,

            **kwargs
        )

    def set_address(
            self,
            private_key: str,
            private_key_type: enums.PrivateKeyType,
            cairo_version: int,
    ):
        if len(private_key) != config.STARK_KEY_LENGTH:
            return

        if private_key_type == enums.PrivateKeyType.braavos:
            address = hex(get_braavos_addr_from_private_key(private_key, cairo_version=cairo_version))
        elif private_key_type == enums.PrivateKeyType.argent:
            address = hex(get_argent_addr_from_private_key(private_key, cairo_version=cairo_version))
        else:
            return

        self.text = address
        self.entry.configure(textvariable=tkinter.StringVar(value=address))
