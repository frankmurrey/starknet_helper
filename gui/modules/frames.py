from gui.modules.swap import SwapTab

import customtkinter


class ModulesFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(
            row=0,
            column=2,
            padx=20,
            pady=20,
            sticky="nsew")
        self.frame.grid_rowconfigure(0, weight=1)

        self.tabview = customtkinter.CTkTabview(self.frame, width=300)
        self.tabview.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="nsew",
            rowspan=7
        )
        self.tabview.grid_columnconfigure(0, weight=1)
        self.set_default_tab()

    def set_default_tab(self):
        tab_name = "Swap"
        self.tabview.add(tab_name)
        self.tabview.set(tab_name)
        SwapTab(
            self.tabview,
            tab_name
        )
