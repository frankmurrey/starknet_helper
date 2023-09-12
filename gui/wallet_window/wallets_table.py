import tkinter.messagebox
from typing import List

import customtkinter

from gui.wallet_window.wallet_item import WalletItem
from gui.wallet_window.frames import WalletsTableTop
from src.schemas.proxy_data import ProxyData
from src.schemas.wallet_data import WalletData


class WalletsTable(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.frame = customtkinter.CTkScrollableFrame(master, width=950)
        self.frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew", rowspan=7)

        self.no_wallets_label = customtkinter.CTkLabel(
            self.frame,
            text="No wallets",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self.no_wallets_label.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

        self.frame.grid_columnconfigure(0, weight=1)

        self.wallets_items: List[WalletItem] = []

        table_grid = {"row": 0, "column": 0, "padx": 20, "pady": (0, 0), "sticky": "ew"}
        self.wallets_table_top = WalletsTableTop(
            master=master, grid=table_grid, wallet_items=self.wallets_items
        )

    @property
    def wallets(self):
        return [wallet_item.wallet_data for wallet_item in self.wallets_items]

    def remove_all_wallets(self):
        if not len(self.wallets):
            return

        for wallet_index, wallet_item in enumerate(self.wallets_items):
            wallet_item.grid_forget()
            wallet_item.frame.destroy()
            wallet_item.destroy()

        self.wallets_items.clear()

    def show_no_wallets_label(self):
        self.no_wallets_label = customtkinter.CTkLabel(
            self.frame,
            text="No wallets, why delete me?",
            font=customtkinter.CTkFont(size=20, weight="bold"),
            corner_radius=10,
        )
        self.no_wallets_label.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

    def destroy_no_wallets_label(self):
        if self.no_wallets_label is None:
            return

        self.no_wallets_label.grid_forget()
        self.no_wallets_label.destroy()
        self.no_wallets_label = None

    def remove_selected_wallets(self):
        new_wallets_data = []
        for wallet_index, wallet_item in enumerate(self.wallets_items):
            wallet_item.grid_forget()
            wallet_item.frame.destroy()
            wallet_item.destroy()

            if not wallet_item.is_chosen:
                new_wallets_data.append(wallet_item.wallet_data)

        self.set_wallets(new_wallets_data)

    def set_wallets(self, wallets: List[WalletData]):
        """
        Set wallets
        Args:
            wallets:

        Returns:

        """

        self.destroy_no_wallets_label()
        self.remove_all_wallets()

        start_row = 0
        start_column = 0

        wallets_items = []
        for wallet_index, wallet_data in enumerate(wallets):
            wallet_item_grid = {
                "row": start_row + 1 + wallet_index,
                "column": start_column,
                "padx": 10,
                "pady": 2,
                "sticky": "ew",
            }

            wallet_item = WalletItem(
                master=self.frame,
                grid=wallet_item_grid,
                wallet_data=wallet_data,
                index=wallet_index,
            )
            wallets_items.append(wallet_item)

        self.wallets_items = wallets_items
        self.wallets_table_top.wallet_items = self.wallets_items

    def add_wallets(self, wallets: List[WalletData]):
        """
        Add wallets to existing wallets
        Args:
            wallets: List of wallets
        Returns: None
        """
        wallets = [*self.wallets, *wallets]
        self.set_wallets(wallets)
