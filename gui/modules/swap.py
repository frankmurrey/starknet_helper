from gui.modules.txn_settings_frame import TxnSettingFrame

import customtkinter
from tkinter import Variable


class SwapTab(customtkinter.CTk):
    def __init__(
            self,
            tabview,
            tab_name
    ):
        super().__init__()
        self.tabview = tabview
        self.tab_name = tab_name

        swap_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 10,
            "sticky": "nsew"
        }

        self.swap_frame = SwapFrame(
            master=self.tabview.tab(tab_name),
            grid=swap_frame_grid
        )

        txn_settings_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": 10,
            "sticky": "nsew"
        }

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid=txn_settings_grid
        )


class SwapFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid
    ):
        super().__init__(master)

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(**grid)
        self.frame.grid_columnconfigure((0, 1), weight=1, uniform="a")
        self.frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

        self.protocol_label = customtkinter.CTkLabel(
            self.frame,
            text="Protocol:"
        )
        self.protocol_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.protocol_combo = customtkinter.CTkComboBox(
            self.frame,
            values=[
                "Uniswap",
                "SushiSwap"
            ]
        )
        self.protocol_combo.grid(
            row=1,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.coin_to_swap_label = customtkinter.CTkLabel(
            self.frame,
            text="Coin to swap:"
        )
        self.coin_to_swap_label.grid(
            row=2,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.coin_to_swap_combo = customtkinter.CTkComboBox(
            self.frame,
            values=[
                "ETH",
                "USDT",
                "USDC"
            ]
        )
        self.coin_to_swap_combo.grid(
            row=3,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.coin_to_receive_label = customtkinter.CTkLabel(
            self.frame,
            text="Coin to receive:"
        )
        self.coin_to_receive_label.grid(
            row=2,
            column=1,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.coin_to_receive_combo = customtkinter.CTkComboBox(
            self.frame,
            values=[
                "ETH",
                "USDT",
                "USDC"
            ]
        )
        self.coin_to_receive_combo.grid(
            row=3,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.min_amount_label = customtkinter.CTkLabel(
            self.frame,
            text="Min amount:"
        )
        self.min_amount_label.grid(
            row=4,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.min_amount_entry = customtkinter.CTkEntry(
            self.frame,
            width=140
        )
        self.min_amount_entry.grid(
            row=5,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.max_amount_label = customtkinter.CTkLabel(
            self.frame,
            text="Max amount:"
        )
        self.max_amount_label.grid(
            row=4,
            column=1,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.max_amount_entry = customtkinter.CTkEntry(
            self.frame,
            width=140
        )
        self.max_amount_entry.grid(
            row=5,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.use_all_balance_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Use all balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.use_all_balance_checkbox_event
        )
        self.use_all_balance_checkbox.grid(
            row=6,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky="w"
        )

        self.send_percent_balance_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Send % of balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18
        )
        self.send_percent_balance_checkbox.grid(
            row=7,
            column=0,
            padx=20,
            pady=(5, 0),
            sticky="w"
        )

        self.slippage_label = customtkinter.CTkLabel(
            self.frame,
            text="Slippage (%):"
        )
        self.slippage_label.grid(
            row=8,
            column=1,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.slippage_entry = customtkinter.CTkEntry(
            self.frame,
            width=70
        )
        self.slippage_entry.grid(
            row=9,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.max_price_difference_percent_label = customtkinter.CTkLabel(
            self.frame,
            text="Max price difference (%):"
        )
        self.max_price_difference_percent_label.grid(
            row=8,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.max_price_difference_percent_entry = customtkinter.CTkEntry(
            self.frame,
            width=70,
            textvariable=Variable(value=2)
        )
        self.max_price_difference_percent_entry.grid(
            row=9,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.compare_with_cg_price_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="Compare to Gecko price",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.compare_with_cg_price_checkbox_event
        )
        self.compare_with_cg_price_checkbox.grid(
            row=10,
            column=0,
            padx=20,
            pady=10,
            sticky="w"
        )
        self.compare_with_cg_price_checkbox.select()

    def use_all_balance_checkbox_event(self):
        if self.use_all_balance_checkbox.get():
            self.min_amount_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.configure(
                state="disabled"
            )
        else:
            self.min_amount_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.configure(
                state="normal"
            )

    def compare_with_cg_price_checkbox_event(self):
        if self.compare_with_cg_price_checkbox.get():
            self.max_price_difference_percent_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value=2)
            )
        else:
            self.max_price_difference_percent_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )







