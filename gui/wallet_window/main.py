import tkinter.messagebox
import tkinter.filedialog

import customtkinter

from gui.wallet_window.wallets_table import WalletsTable

from src.wallet_manager import WalletManager
from utlis.file_manager import FileManager
from src import paths


class WalletsWindow(customtkinter.CTkFrame):
    def __init__(self, master: any, **kwargs):
        super().__init__(master, **kwargs)

        self.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.grid_columnconfigure(0,  weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)

        self.wallets_table = WalletsTable(self)

        self.import_button = customtkinter.CTkButton(
            self,
            text="Import",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=70,
            height=30,
            command=self.load_wallets_csv_file
        )
        self.import_button.grid(row=8, column=0, padx=20, pady=10, sticky="wn")

        self.remove_button = customtkinter.CTkButton(
            self,
            text="Remove all",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            fg_color="#cc0000",
            hover_color="#5e1914",
            width=70,
            height=30,
            command=self.remove_all_wallets
        )
        self.remove_button.grid(row=8, column=0, padx=100, pady=10, sticky="wn")

    @property
    def wallets(self):
        return [wallet_item.wallet_data for wallet_item in self.wallets_table.wallets_items]

    def load_wallets_csv_file(self):
        filepath = tkinter.filedialog.askopenfilename(
            initialdir=paths.MAIN_DIR,
            title="Select wallets csv file",
            filetypes=[("Text files", "*.csv")]
        )

        if not filepath:
            return

        wallets_raw_data = FileManager.read_data_from_csv_file(filepath)
        wallets = WalletManager.get_wallets(wallets_raw_data)
        self.wallets_table.set_wallets(wallets)

    def remove_selected_wallets(self):
        # TODO: Ебланский способ

        new_wallets_data = []
        for wallet_index, wallet_item in enumerate(self.wallets_table.wallets_items):
            wallet_item.grid_forget()
            wallet_item.frame.destroy()
            wallet_item.destroy()

            if not wallet_item.is_chosen:
                new_wallets_data.append(wallet_item.wallet_data)

        self.wallets_table.set_wallets(new_wallets_data)

    def remove_all_wallets(self):
        if not self.wallets:
            return

        msg_box = tkinter.messagebox.askyesno(
            title="Remove all",
            message="Are you sure you want to remove all wallets?",
            icon="warning"
        )

        if not msg_box:
            return

        for wallet_index, wallet_item in enumerate(self.wallets_table.wallets_items):
            wallet_item.grid_forget()
            wallet_item.frame.destroy()
            wallet_item.destroy()

        self.wallets_table.set_wallets([])

