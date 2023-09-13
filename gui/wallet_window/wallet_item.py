import customtkinter

from src.schemas.wallet_data import WalletData
from utlis.key_manager.key_manager import get_argent_addr_from_private_key
from utlis.key_manager.key_manager import get_braavos_addr_from_private_key
from src import enums


class WalletItem(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid: dict,
            wallet_data: WalletData,
            index: int,):

        super().__init__(master)

        self.wallet_data = wallet_data
        self.index = index

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(**grid)

        self.frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="uniform")

        self.frame.grid_rowconfigure(0, weight=1)

        pad_x = (40, 0)
        kf = 0

        pad_y = 5

        self.chose_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="",
            checkbox_width=20,
            checkbox_height=20,
            onvalue=True,
            offvalue=False
        )
        self.chose_checkbox.grid(
            row=0,
            column=0,
            padx=(10, 0),
            pady=pad_y,
            sticky="w",
        )

        self.wallet_name_label = customtkinter.CTkLabel(
            self.frame,
            text=wallet_data.name if wallet_data.name is not None else f"Wallet {index + 1}",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.wallet_name_label.grid(
            row=0,
            column=0,
            padx=(50, 0),
            pady=pad_y,
            sticky="w"
        )

        self.wallet_address_label = customtkinter.CTkLabel(
            self.frame,
            text=self.get_short_address(wallet_data.address),
            font=customtkinter.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.wallet_address_label.grid(
            row=0,
            column=1,
            padx=0,
            pady=pad_y,
        )

        self.proxy_address_label = customtkinter.CTkLabel(
            self.frame,
            text=self.get_short_proxy(host='http://192.168.321.23.1',
                                      port='12345'),
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.proxy_address_label.grid(
            row=0,
            column=2,
            padx=(30, 0),
            pady=pad_y,
            sticky="w"
        )

        self.wallet_type_label = customtkinter.CTkLabel(
            self.frame,
            text=wallet_data.type.title(),
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.wallet_type_label.grid(
            row=0,
            column=3,
            padx=(100, 0),
            pady=pad_y,
            sticky="w"
        )

        self.edit_button = customtkinter.CTkButton(
            self.frame,
            text="Edit",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=45,
            height=25,
        )
        self.edit_button.grid(
            row=0,
            column=4,
            padx=(0, 80),
            pady=pad_y,
            sticky="e"
        )

    @property
    def is_chosen(self):
        return self.chose_checkbox.get()

    @staticmethod
    def get_short_address(
            address: str
    ):
        return address[:6] + "..." + address[-4:]

    @staticmethod
    def get_short_proxy(
            host: str,
            port: str
    ):
        if "//" in host:
            host = host.split("//")[1]

        # proxy = host[:8] + " " + ":" + port
        proxy = host + port

        return proxy
