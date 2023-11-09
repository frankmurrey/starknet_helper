import tkinter
import tkinter.messagebox

import customtkinter

from gui import objects, constants
from utils.proxy import parse_proxy_data


class ProxyEntry(objects.CTkEntryWithLabel):
    def __init__(
            self,
            master,
            proxy: str,
            **kwargs
    ):
        super().__init__(
            master,
            label_text="Proxy",
            textvariable=tkinter.StringVar(value=proxy),
            width=200,

            hide_on_focus_out=True,

            on_text_changed=self.proxy_changed,

            **kwargs
        )

        # INVALID LABEL
        self.info_label = customtkinter.CTkLabel(
            self,
            text="",
            text_color=constants.ERROR_HEX,
        )
        self.info_label.grid(row=1, column=1, padx=10, pady=0, sticky="w")

        self.proxy_data = None

    @property
    def proxy(self):
        return self.text

    def set_invalid_label(self):
        self.info_label.configure(
            text="Invalid proxy",
            text_color=constants.ERROR_HEX,
        )

    def set_socks5_label(self):
        auth = 'auth' if self.proxy_data.auth else 'no auth'
        self.info_label.configure(
            text=f"SOCKS5 {auth}",
            text_color=constants.SUCCESS_HEX,
        )

    def set_http_label(self):
        auth = 'auth' if self.proxy_data.auth else 'no auth'
        self.info_label.configure(
            text=f"HTTP {auth}",
            text_color=constants.SUCCESS_HEX,
        )

    def set_empty_label(self):
        self.info_label.configure(
            text="",
        )

    def proxy_changed(self):
        self.proxy_data = parse_proxy_data(self.proxy)
        if self.proxy_data is None:
            self.set_invalid_label()
            return

        if self.proxy_data.proxy_type == "socks5":
            self.set_socks5_label()

        elif self.proxy_data.proxy_type == "http":
            self.set_http_label()

        else:
            self.set_invalid_label()


