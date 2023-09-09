import customtkinter


class WalletsTableTop(customtkinter.CTkFrame):
    def __init__(self,
                 master,
                 grid,
                 wallet_items: list):
        super().__init__(master)

        self.wallet_items = wallet_items

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(**grid)

        self.frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="a")

        self.chose_all_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="",
            checkbox_width=20,
            checkbox_height=20,
            onvalue=True,
            offvalue=False,
            command=self.select_all_checkbox_event
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

    def select_all_checkbox_event(self):
        print(self.wallet_items)

        checkbox_value = self.chose_all_checkbox.get()
        if checkbox_value:
            for wallet in self.wallet_items:
                wallet.chose_checkbox.select()

        else:
            for wallet in self.wallet_items:
                wallet.chose_checkbox.deselect()
