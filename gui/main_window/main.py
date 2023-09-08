import customtkinter
import webbrowser

from utlis.file_manager import FileManager
from src.storage import Storage
from src import paths
from gui.main_window.frames import SidebarFrame
from gui.wallet_window.main import WalletsFrame
from gui.wallet_window.frames import WalletTableTop

from tkinter import messagebox, filedialog
from PIL import Image


def run_gui():
    window = MainWindow()
    window.mainloop()


class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("StarkNet Helper by @frankmurrey")

        self.geometry(f"{1280}x{720}+100+100")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.sidebar_frame = SidebarFrame(self)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.right_frame = customtkinter.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)

        self.wallet_frame = WalletsFrame(
            self.right_frame)

        self.upload_button = customtkinter.CTkButton(
            self.right_frame,
            text="Upload",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=70,
            height=30
        )
        self.upload_button.grid(row=8, column=0, padx=20, pady=10, sticky="wn")

        self.remove_button = customtkinter.CTkButton(
            self.right_frame,
            text="Remove",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            fg_color="#cc0000",
            hover_color="#5e1914",
            width=70,
            height=30
        )
        self.remove_button.grid(row=8, column=0, padx=100, pady=10, sticky="wn")



