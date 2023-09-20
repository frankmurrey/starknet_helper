import customtkinter

from gui.main_window.frames import SidebarFrame
from gui.wallet_right_window.right_frame import RightFrame


def run_gui():
    window = MainWindow()
    window.mainloop()


class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        self.title("StarkNet Helper by @frankmurrey")

        self.geometry(f"{1200}x{900}+100+100")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)

        self.sidebar_frame = SidebarFrame(self)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.right_frame = RightFrame(self)




