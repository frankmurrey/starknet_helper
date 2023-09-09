import customtkinter

from src.schemas.wallet_data import WalletData
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

        self.frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="a")
        self.frame.grid_rowconfigure(0, weight=1)

        pad_x = 50
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
            padx=10,
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
            padx=pad_x,
            pady=pad_y,
            sticky="w"
        )

        pad_x = pad_x + kf

        self.wallet_address_label = customtkinter.CTkLabel(
            self.frame,
            text=wallet_data.private_key,
            font=customtkinter.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        self.wallet_address_label.grid(
            row=0,
            column=1,
            padx=(0, pad_x * 2),
            pady=pad_y,
        )

        pad_x = pad_x + kf

        proxy = f"{wallet_data.proxy.host}:{wallet_data.proxy.port}" if wallet_data.proxy else "-"
        self.proxy_address_label = customtkinter.CTkLabel(
            self.frame,
            text=proxy,
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.proxy_address_label.grid(
            row=0,
            column=2,
            padx=pad_x,
            pady=pad_y,
            sticky="w"
        )

        pad_x = pad_x + kf

        self.wallet_type_label = customtkinter.CTkLabel(
            self.frame,
            text=wallet_data.type.title(),
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.wallet_type_label.grid(
            row=0,
            column=3,
            padx=pad_x,
            pady=pad_y,
            sticky="w"
        )

        pad_x = pad_x + kf

        self.edit_button = customtkinter.CTkButton(
            self.frame,
            text="Edit",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=45,
            height=25,
        )
        self.edit_button.grid(
            row=0,
            column=3,
            padx=pad_x,
            pady=pad_y,
            sticky="e"
        )

    @property
    def is_chosen(self):
        return self.chose_checkbox.get()
