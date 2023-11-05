import customtkinter
import webbrowser
import asyncio
from threading import Thread

from src import paths
from src.gecko_pricer import GeckoPricer
from gui.main_window.tools_window import ToolsWindow
from gui.main_window.settings_window import SettingsWindow
from utils.gas_price import GasPrice, get_eth_mainnet_gas_price

from PIL import Image


class SidebarFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            **kwargs
    ):
        super().__init__(master, **kwargs)
        self.master = master

        self.tools_window = None
        self.settings_window = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 4, 5, 6, 7, 8), weight=0)
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
            size=(150, 90)
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
        self.tools_button = customtkinter.CTkButton(
            self,
            text="Tools",
            command=self.tools_button_event,
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.tools_button.grid(
            row=1,
            column=0,
            padx=25,
            pady=(10, 20),
            sticky="w"
        )

        self.settings_button = customtkinter.CTkButton(
            self,
            text="Settings",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            command=self.settings_button_event
        )
        self.settings_button.grid(
            row=2,
            column=0,
            padx=25,
            pady=(0, 20),
            sticky="w"
        )

        self.price_frame = PriceFrame(
            self,
            grid={
                "row": 3,
                "column": 0,
                "padx": 20,
                "pady": 0,
                "sticky": "w"
            },
        )

        # REFRESH BUTTON
        refresh_image = customtkinter.CTkImage(
            light_image=Image.open(f"{paths.GUI_DIR}/images/refresh_button.png"),
            dark_image=Image.open(f"{paths.GUI_DIR}/images/refresh_button.png"),
            size=(20, 20)
        )
        self.refresh_button = customtkinter.CTkButton(
            self,
            image=refresh_image,
            command=self.price_frame.set_gas_data,
            hover=False,
            text="- refresh data",
            bg_color='transparent',
            fg_color='transparent',
            width=5,
            text_color='gray58',

        )
        self.refresh_button.grid(
            row=4,
            column=0,
            padx=(18, 0),
            pady=(0, 2),
            sticky="w"
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
            text="v1.1.0 Github origin",
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

    def tools_button_event(self):
        geometry = "450x900+1505+100"
        if self.winfo_screenwidth() <= 1600:
            geometry = "450x450+1050+100"

        if self.tools_window is None or not self.tools_window.winfo_exists():
            self.tools_window = ToolsWindow(self)
            self.tools_window.geometry(geometry)
            self.tools_window.resizable(False, False)
        else:
            self.tools_window.focus()

    def settings_button_event(self):
        geometry = "450x900+1505+100"
        if self.winfo_screenwidth() <= 1600:
            geometry = "450x600+1050+100"

        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
            self.settings_window.geometry(geometry)
            self.settings_window.resizable(False, False)
        else:
            self.settings_window.focus()


class PriceFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any,
            grid: dict,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.master = master

        self.grid(**grid)
        self.grid_columnconfigure((0, 1,), weight=1, uniform="uniform")
        self.grid_rowconfigure((0, 1, 2, 3), weight=0)

        # STARK GAS
        self.stark_gas_price_label = customtkinter.CTkLabel(
            self,
            text="Stark Gas:",
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.stark_gas_price_label.grid(
            row=0,
            column=0,
            padx=(10, 0),
            pady=2,
            sticky="w"
        )

        self.stark_gas_price_value_label = customtkinter.CTkLabel(
            self,
            text="N/A",
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.stark_gas_price_value_label.grid(
            row=0,
            column=1,
            padx=(10, 0),
            pady=(0, 2),
            sticky="w"
        )

        # L1 ETH GAS
        self.l1_eth_gas_price_label = customtkinter.CTkLabel(
            self,
            text="ETH Gas:",
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.l1_eth_gas_price_label.grid(
            row=1,
            column=0,
            padx=(10, 0),
            pady=2,
            sticky="w"
        )

        self.l1_eth_gas_price_value_label = customtkinter.CTkLabel(
            self,
            text="N/A",
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )

        self.l1_eth_gas_price_value_label.grid(
            row=1,
            column=1,
            padx=(10, 0),
            pady=(0, 2),
            sticky="w"
        )

        # ETH PRICE
        self.eth_price_label = customtkinter.CTkLabel(
            self,
            text="ETH Price:",
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.eth_price_label.grid(
            row=2,
            column=0,
            padx=(10, 0),
            pady=2,
            sticky="w"
        )

        self.eth_price_value_label = customtkinter.CTkLabel(
            self,
            text="N/A",
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.eth_price_value_label.grid(
            row=2,
            column=1,
            padx=(10, 0),
            pady=(0, 2),
            sticky="w"
        )
        self.set_gas_data()

    def fetch_gas_data(self) -> tuple[str, str, str]:
        stark_gp = GasPrice(block_number='pending')

        loop = asyncio.get_event_loop()
        stark_gas_price = loop.run_until_complete(stark_gp.get_stark_block_gas_price())

        if stark_gas_price is None:
            stark_gas_price = "N/A"
        else:
            stark_gas_price = round(stark_gas_price / 10 ** 9, 2)

        l1_gas_price = get_eth_mainnet_gas_price('https://rpc.ankr.com/eth')
        if l1_gas_price is None:
            l1_gas_price = "N/A"

        eth_price = GeckoPricer.get_simple_price_of_token_sync("ethereum")
        if eth_price is None:
            eth_price = "N/A"

        return str(stark_gas_price), str(l1_gas_price), str(eth_price)

    def set_gas_data(self):

        def _(loop):
            asyncio.set_event_loop(loop)

            try:
                stark_gas_price, l1_gas_price, eth_price = self.fetch_gas_data()
                self.stark_gas_price_value_label.configure(text=stark_gas_price)
                self.l1_eth_gas_price_value_label.configure(text=l1_gas_price)
                self.eth_price_value_label.configure(text=eth_price)
            except RuntimeError as e:
                pass

        Thread(
            target=_,
            args=(asyncio.get_event_loop(), ),
            name="gas_price_thread"
        ).start()

