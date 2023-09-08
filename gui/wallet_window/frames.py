from src.schemas.wallet_data import WalletData
from src import enums

import customtkinter


class WalletItem(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid: dict,
            wallet_data: WalletData,
            name: str):

        super().__init__(master)

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
            text=name,
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


class WalletTableTop(customtkinter.CTkFrame):
    def __init__(self,
                 master,
                 grid):
        super().__init__(master)

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(**grid)

        self.frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="a")

        self.chose_all_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="",
            checkbox_width=20,
            checkbox_height=20,
            onvalue=True,
            offvalue=False
        )

        pad_x = 50
        kf = 0
        pad_y = 5

        self.chose_all_checkbox.grid(
            row=0,
            column=0,
            padx=25,
            pady=5,
            sticky="w"
        )

        self.wallet_name_label = customtkinter.CTkLabel(
            self.frame,
            text="Name",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.wallet_name_label.grid(
            row=0,
            column=0,
            padx=pad_x + 15,
            pady=pad_y,
            sticky="w"
        )

        pad_x = pad_x + kf

        self.wallet_address_label = customtkinter.CTkLabel(
            self.frame,
            text="Address",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        self.wallet_address_label.grid(
            row=0,
            column=1,
            padx=pad_x - 8,
            pady=pad_y,
            sticky="w"
        )

        pad_x = pad_x + kf

        self.wallet_proxy_label = customtkinter.CTkLabel(
            self.frame,
            text="Proxy",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        self.wallet_proxy_label.grid(
            row=0,
            column=2,
            padx=pad_x,
            pady=pad_y,
            sticky="w"
        )

        pad_x = pad_x + kf

        self.wallet_type_label = customtkinter.CTkLabel(
            self.frame,
            text="Type",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        self.wallet_type_label.grid(
            row=0,
            column=3,
            padx=pad_x - 10,
            pady=pad_y,
            sticky="w"
        )



