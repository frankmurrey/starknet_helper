import sys

import customtkinter

from src.tasks_executor import tasks_executor
from src.logger import configure_logger

from gui.main_window.frames import SidebarFrame
from gui.wallet_right_window.right_frame import RightFrame

from utils.repr.misc import print_logo
from src.templates.templates import Templates


def run_gui():
    window = MainWindow()
    try:
        window.mainloop()
    except KeyboardInterrupt:
        window.on_closing()


class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.on_start()

        self.resizable(False, False)
        if self.winfo_screenheight() < 950:
            self.resizable(False, True)

        self.title("StarkNet Helper by @frankmurrey")

        self.geometry(f"{1400}x{900}+100+100")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)

        self.sidebar_frame = SidebarFrame(self)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.right_frame = RightFrame(self)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_start(self):
        configure_logger()
        Templates().create_not_found_temp_files()
        print_logo()

    def on_closing(self):
        tasks_executor.stop()
        self.destroy()
        self.quit()

        sys.exit()
