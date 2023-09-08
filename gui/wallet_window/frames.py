import customtkinter


class WalletItem(customtkinter.CTkFrame):
    def __init__(
            self,
            master):
        super().__init__(master, height=50)

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(
            row=0,
            column=0,
            padx=10,
            pady=10,
            sticky="nsew"
        )

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
            pady=10,
            sticky="w"
        )

        self.wallet_name_label = customtkinter.CTkLabel(
            self.frame,
            text="Wallet name",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.wallet_name_label.grid(
            row=0,
            column=0,
            padx=50,
            pady=10,
            sticky="w"
        )

        self.wallet_address_label = customtkinter.CTkLabel(
            self.frame,
            text="Wallet address",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.wallet_address_label.grid(
            row=0,
            column=1,
            padx=50,
            pady=10,
            sticky="w"
        )

        self.proxy_address_label = customtkinter.CTkLabel(
            self.frame,
            text="Proxy address",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.proxy_address_label.grid(
            row=0,
            column=2,
            padx=50,
            pady=10,
            sticky="w"
        )


