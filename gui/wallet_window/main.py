from gui.wallet_window.frames import WalletItem
from gui.wallet_window.frames import WalletTableTop
from src.schemas.wallet_data import WalletData
from src.schemas.wallet_data import ProxyData

import customtkinter


class WalletsFrame(customtkinter.CTkScrollableFrame):
    def __init__(
            self,
            master,
            **kwargs):
        super().__init__(master, **kwargs)

        self.frame = customtkinter.CTkScrollableFrame(master)
        self.frame.grid(
            row=1,
            column=0,
            padx=20,
            pady=0,
            sticky="nsew",
            rowspan=7
        )

        self.frame.grid_columnconfigure(0, weight=1)

        start_row = 0
        start_column = 0

        proxy = ProxyData(
            host="host",
            port=8080,
            username="username",
            password="password",
            auth=True,
            is_mobile=False
        )

        wallet_item = WalletData(
            private_key="0x0000000",
            proxy=proxy,
            type="Argent"
        )
        all_wallet_items = []
        for i in range(4):
            wallet_item_grid = {
                "row": start_row + 1 + i,
                "column": start_column,
                "padx": 10,
                "pady": 2,
                "sticky": "ew"
            }

            self.wallet_item = WalletItem(master=self.frame,
                                          grid=wallet_item_grid,
                                          wallet_data=wallet_item,
                                          name=f"Wallet {i + 1}")
            all_wallet_items.append(self.wallet_item)

        table_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": (0, 0),
            "sticky": "ew"
        }
        self.table_frame = WalletTableTop(master=master,
                                          grid=table_grid,
                                          wallet_items=all_wallet_items)
