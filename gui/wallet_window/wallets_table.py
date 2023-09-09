from typing import List

import customtkinter

from gui.wallet_window.wallet_item import WalletItem
from gui.wallet_window.frames import WalletsTableTop
from src.schemas.proxy_data import ProxyData
from src.schemas.wallet_data import WalletData


class WalletsTable(customtkinter.CTkScrollableFrame):
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

        self.no_wallets_label = customtkinter.CTkLabel(
            self.frame,
            text="No wallets",
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        self.no_wallets_label.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

        self.frame.grid_columnconfigure(0, weight=1)

        self.wallets_items: List[WalletItem] = []

        table_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": (0, 0),
            "sticky": "ew"
        }
        self.wallets_table_top = WalletsTableTop(master=master,
                                                 grid=table_grid,
                                                 wallet_items=self.wallets_items)

    def set_wallets(self, wallets: List[WalletData]):
        if not wallets:
            self.no_wallets_label = customtkinter.CTkLabel(
                self.frame,
                text="No wallets, why delete me?",
                font=customtkinter.CTkFont(size=16, weight="bold"),
                corner_radius=10
            )
            self.no_wallets_label.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        else:
            self.no_wallets_label.grid_forget()
            self.no_wallets_label.destroy()

        start_row = 0
        start_column = 0

        wallets_items = []
        for wallet_index, wallet_data in enumerate(wallets):
            wallet_item_grid = {
                "row": start_row + 1 + wallet_index,
                "column": start_column,
                "padx": 10,
                "pady": 2,
                "sticky": "ew"
            }

            wallet_item = WalletItem(master=self.frame,
                                     grid=wallet_item_grid,
                                     wallet_data=wallet_data,
                                     index=wallet_index)
            wallets_items.append(wallet_item)

        self.wallets_items = wallets_items
        self.wallets_table_top.wallet_items = self.wallets_items
