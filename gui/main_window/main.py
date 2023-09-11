import customtkinter
import webbrowser

from utlis.file_manager import FileManager
from src.storage import Storage
from src import paths
from gui.main_window.frames import SidebarFrame
from gui.modules.frames import ModulesFrame
from gui.wallet_window.main import WalletsWindow

from tkinter import messagebox, filedialog
from PIL import Image


def run_gui():
    window = MainWindow()
    window.mainloop()


class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("StarkNet Helper by @frankmurrey")

        self.geometry(f"{1280}x{1000}+100+100")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)

        self.sidebar_frame = SidebarFrame(self)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.right_frame = WalletsWindow(self)




