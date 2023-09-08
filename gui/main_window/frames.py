import customtkinter
import webbrowser

from src import paths
from gui import constants

from PIL import Image


class SidebarFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.frame = customtkinter.CTkFrame(
            master=self,
            width=150,
            height=900,
            corner_radius=0
        )
        self.frame.grid(row=0,
                        column=0,
                        sticky="nsw"
                        )
        self.tabview = customtkinter.CTkTabview(
            self,
            width=400,
            height=840,
            bg_color="transparent"
        )
        logo_image = customtkinter.CTkImage(
            light_image=Image.open(paths.LIGHT_MODE_LOGO_IMG),
            dark_image=Image.open(paths.DARK_MODE_LOGO_IMG),
            size=(150, 85)
        )
        self.logo_label = customtkinter.CTkLabel(
            self.frame,
            image=logo_image,
            text=""
        )
        self.logo_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 10)
        )
        self.wallets_button = customtkinter.CTkButton(
            self.frame,
            text="Wallets",
            font=customtkinter.CTkFont(
                size=14,
                weight="bold"
            ),
            width=140,
            anchor="c"
        )
        self.wallets_button.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 450)
        )

        self.appearance_mode_label = customtkinter.CTkLabel(
            self.frame,
            text="Appearance Mode:",
            anchor="w")
        self.appearance_mode_label.grid(
            row=9,
            column=0,
            padx=20,
            pady=(0, 75)
        )
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.frame,
            values=["Dark", "Light", "System"],
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
            self.frame,
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
        webbrowser.open("https://github.com/frankmurrey/starknet_drop_helper")