import tkinter.messagebox
from typing import Callable, Union

from gui.modules.swap import SwapTab
from gui.modules.add_liquidity import AddLiquidityTab
from gui.modules.remove_liquidity import RemoveLiquidityTab
from gui.modules.supply import SupplyLendingTab

import customtkinter


class InteractionTopLevelWindow(customtkinter.CTkToplevel):
    def __init__(
            self,
            parent,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.title("New action")
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)

        self.parent = parent

        self.chose_module_frame = ChoseModuleFrame(
            master=self
        )

        self.tabview = customtkinter.CTkTabview(
            self,
            width=300,
            height=600
        )
        self.tabview.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="nsew"
        )
        self.tabview.grid_columnconfigure(0, weight=1)

        self.current_tab_name = None
        self.current_tab = None
        self.set_default_tab()

        self.confirm_button = customtkinter.CTkButton(
            self,
            text="Add",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=100,
            height=35,
            command=self.confirm_button_event
        )
        self.confirm_button.grid(
            row=2,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="w"
        )

    def set_new_tab(
            self,
            tab_name: str):
        if self.current_tab_name is not None:
            self.tabview.delete(self.current_tab_name.title())

        self.tabview.add(tab_name)
        self.tabview.set(tab_name)

        if tab_name == "Swap":
            self.current_tab = SwapTab(
                self.tabview,
                tab_name
            )
            self.current_tab_name = tab_name

        elif tab_name == "Add Liquidity":
            self.current_tab = AddLiquidityTab(
                self.tabview,
                tab_name
            )
            self.current_tab_name = tab_name

        elif tab_name == "Remove Liquidity":
            self.current_tab = RemoveLiquidityTab(
                self.tabview,
                tab_name
            )
            self.current_tab_name = tab_name

        elif tab_name == "Supply Lending":
            self.current_tab = SupplyLendingTab(
                self.tabview,
                tab_name
            )
            self.current_tab_name = tab_name

    def set_default_tab(self):
        tab_name = self.chose_module_frame.modules_option_menu.get()
        self.tabview.add(tab_name.title())
        self.tabview.set(tab_name.title())
        self.current_tab = SwapTab(
            self.tabview,
            tab_name
        )
        self.current_tab_name = tab_name

    def get_repeats_amount(self) -> Union[int, None]:
        try:
            repeats = int(self.chose_module_frame.float_spinbox.get())
            if repeats < 1:
                return None
            return repeats

        except ValueError:
            return None

    def confirm_button_event(self):
        current_tab = self.current_tab
        if current_tab is None:
            return

        config_data = current_tab.build_config_data()
        if config_data is None:
            return

        repeats = self.get_repeats_amount()
        if repeats is None:
            tkinter.messagebox.showerror(
                title="Error",
                message="Repeats amount must be a positive integer"
            )
            return

        self.parent.set_action(
            {
                "config_data": config_data,
                "repeats": repeats
            }
        )


class ChoseModuleFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master
    ):
        super().__init__(master=master)
        self.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="nsew"

        )
        self.label = customtkinter.CTkLabel(
            self,
            text="Module:",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(5, 0),
            sticky="w"
        )

        self.modules_option_menu = customtkinter.CTkOptionMenu(
            self,
            values=[
                'Swap',
                "Add Liquidity",
                "Remove Liquidity",
                "Supply Lending",
                "Withdraw Lending",
            ],
            command=master.set_new_tab
        )
        self.modules_option_menu.grid(
            row=1,
            column=0,
            padx=20,
            pady=(5, 20),
            sticky="w"
        )

        self.actions_amount_label = customtkinter.CTkLabel(
            self,
            text="Repeats:",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.actions_amount_label.grid(
            row=0,
            column=1,
            padx=20,
            pady=(5, 0),
            sticky="w"
        )

        self.float_spinbox = FloatSpinbox(master=self)
        self.float_spinbox.grid(
            row=1,
            column=1,
            padx=20,
            pady=(5, 20),
            sticky="w"
        )


class FloatSpinbox(customtkinter.CTkFrame):
    def __init__(
            self,
            *args,
            width: int = 100,
            height: int = 32,
            step_size: Union[int, float] = 1,
            command: Callable = None,
            **kwargs
    ):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = int(step_size)
        self.command = command

        self.configure(fg_color=("gray78", "gray21"))

        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0, fg_color="gray16")
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        self.entry.insert(0, "1")

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) - self.step_size
            if value < 1:
                value = 1
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def get(self) -> Union[float, None]:
        try:
            return float(self.entry.get())
        except ValueError:
            return None

    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(int(value)))
