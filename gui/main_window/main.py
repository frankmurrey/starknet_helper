import customtkinter
import webbrowser

from utlis.file_manager import FileManager
from src.storage import Storage
from src import paths

from tkinter import messagebox, filedialog
from PIL import Image


def run_gui():
    window = MainWindow()
    window.mainloop()


class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("StarkNet Helper by @frankmurrey")

        self.geometry(f"{700}x{900}+100+100")

        self.sidebar_frame = customtkinter.CTkFrame(
            self,
            width=150,
            corner_radius=0
        )
        self.sidebar_frame.grid(row=0,
                                column=0,
                                rowspan=4,
                                sticky="nsew"
                                )
        self.sidebar_frame.grid_rowconfigure(
            7,
            weight=1
        )
        logo_image = customtkinter.CTkImage(
            light_image=Image.open(paths.LIGHT_MODE_LOGO_IMG),
            dark_image=Image.open(paths.DARK_MODE_LOGO_IMG),
            size=(150, 85)
        )

        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame,
            image=logo_image,
            text=""
        )
        self.logo_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 10)
        )

        self.tabview = customtkinter.CTkTabview(
            self,
            width=400,
            height=840,
            bg_color="transparent"
        )

        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame,
            text="Appearance Mode:",
            anchor="w")
        self.appearance_mode_label.grid(
            row=9,
            column=0,
            padx=20,
            pady=(0, 75)
        )
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(
            row=9,
            column=0,
            padx=20,
            pady=(0, 20)
        )

        link_font = customtkinter.CTkFont(
            size=12,
            underline=True
        )
        self.github_button = customtkinter.CTkButton(
            self.sidebar_frame,
            text="Github origin",
            font=link_font,
            width=140,
            anchor="c",
            text_color="grey",
            fg_color='transparent',
            hover=False,
            command=self.open_github
        )
        self.github_button.grid(
            row=9,
            column=0,
            padx=20,
            pady=(40, 0)
        )

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def open_github(self):
        webbrowser.open("https://github.com/frankmurrey/aptos_drop_helper")