import customtkinter
import webbrowser

from src import paths
from gui.modules.swap import SwapTab

from PIL import Image


class SidebarFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=0)
        self.grid_rowconfigure(9, weight=1)
        self.grid(
            row=0,
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
            self,
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
            self,
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
            pady=(20, 0)
        )

        self.swaps_button = customtkinter.CTkButton(
            self,
            text="Swaps",
            font=customtkinter.CTkFont(
                size=14,
                weight="bold"
            ),
            width=140,
            anchor="c",
            command=self.swaps_button_event
        )
        self.swaps_button.grid(
            row=2,
            column=0,
            padx=20,
            pady=(20, 0)
        )

        self.liquidity_button = customtkinter.CTkButton(
            self,
            text="Liquidity",
            font=customtkinter.CTkFont(
                size=14,
                weight="bold"
            ),
            width=140,
            anchor="c",
            command=self.liquidity_button_event
        )
        self.liquidity_button.grid(
            row=3,
            column=0,
            padx=20,
            pady=(20, 0)
        )

        self.appearance_mode_label = customtkinter.CTkLabel(
            self,
            text="Appearance Mode:",
            anchor="w")
        self.appearance_mode_label.grid(
            row=9,
            column=0,
            padx=20,
            pady=(0, 80),
            sticky="s"
        )
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(
            row=9,
            column=0,
            padx=20,
            pady=(0, 50),
            sticky="s"
        )

        link_font = customtkinter.CTkFont(
            size=12,
            underline=True
        )
        self.github_button = customtkinter.CTkButton(
            self,
            text="v0.0.0 Github origin",
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
            pady=(0, 10),
            sticky="s"
        )

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def open_github(self):
        webbrowser.open("https://github.com/frankmurrey/starknet_drop_helper")

    def add_new_module_tab(
            self,
            module_name: str
    ):
        """
        Add new module tab to the tabview
        :param module_name: tab name
        :return: 
        """
        self.master.modules_frame.tabview.add(module_name.title())
        self.master.modules_frame.tabview.set(module_name.title())

    def swaps_button_event(self):
        tab_name = "Swap"
        try:
            self.add_new_module_tab(tab_name)
            SwapTab(
                tabview=self.master.modules_frame.tabview,
                tab_name=tab_name
            )

        except ValueError:
            self.master.modules_frame.tabview.set(tab_name)

    def liquidity_button_event(self):
        try:
            self.master.modules_frame.tabview.add("Liquidity")
            self.master.modules_frame.tabview.set("Liquidity")
        except ValueError:
            self.master.modules_frame.tabview.set("Liquidity")
