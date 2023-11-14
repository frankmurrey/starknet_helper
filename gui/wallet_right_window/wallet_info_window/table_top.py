import customtkinter


class WalletInfoTopFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.grid(**grid)

        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="uniform")
        self.grid_rowconfigure(0, weight=1)

        self.action_name_label = customtkinter.CTkLabel(
            self,
            text="Action",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.action_name_label.grid(
            row=0,
            column=0,
            padx=(20, 0),
            pady=5,
            sticky="w",
        )

        self.status_bool_label = customtkinter.CTkLabel(
            self,
            text="Status",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.status_bool_label.grid(
            row=0,
            column=1,
            padx=(0, 0),
            pady=5,
            sticky="w",
        )

        self.status_info_label = customtkinter.CTkLabel(
            self,
            text="Info",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.status_info_label.grid(
            row=0,
            column=2,
            padx=(0, 0),
            pady=5,
            sticky="w",
        )

        self.txn_hash_label = customtkinter.CTkLabel(
            self,
            text="Txn Hash",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.txn_hash_label.grid(
            row=0,
            column=3,
            padx=(0, 0),
            pady=5,
            sticky="w",
        )