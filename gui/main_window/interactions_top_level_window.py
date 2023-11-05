import tkinter.messagebox
from tkinter import Variable
from typing import Callable, Union, TYPE_CHECKING

from gui import modules
from gui.objects import FloatSpinbox
import customtkinter

from src import enums

if TYPE_CHECKING:
    from gui.wallet_right_window.actions_frame import ActionsFrame


class Tab:
    def __init__(
            self,
            tab,
            spinbox_max_value: Union[int, float] = 100,
            spinbox_start_value: Union[int, float] = 1,
    ):
        self.tab = tab
        self.spinbox_max_value = spinbox_max_value
        self.spinbox_start_value = spinbox_start_value


TABS: dict = {
    enums.TabName.SWAP: Tab(
        tab=modules.SwapTab,
    ),
    enums.TabName.ADD_LIQUIDITY: Tab(
        tab=modules.AddLiquidityTab,
    ),
    enums.TabName.REMOVE_LIQUIDITY: Tab(
        tab=modules.RemoveLiquidityTab,
        spinbox_max_value=1,
    ),
    enums.TabName.SUPPLY_LENDING: Tab(
        tab=modules.SupplyLendingTab,
    ),
    enums.TabName.WITHDRAW_LENDING: Tab(
        tab=modules.WithdrawLendingTab,
        spinbox_max_value=1,
    ),
    enums.TabName.MINT: Tab(
        tab=modules.MintTab,
    ),
    enums.TabName.DMAIL_SEND_MAIL: Tab(
        tab=modules.DmailSendMailTab,
    ),
    enums.TabName.DEPLOY: Tab(
        tab=modules.DeployTab,
        spinbox_max_value=1,
    ),
    enums.TabName.UPGRADE: Tab(
        tab=modules.UpgradeTab,
        spinbox_max_value=1,
    ),
    enums.TabName.TRANSFER: Tab(
        tab=modules.TransferTab,
    ),
    enums.TabName.BRIDGE: Tab(
        tab=modules.BridgeTab,
    ),
    enums.TabName.TRASH_TXNS: Tab(
        tab=modules.TrashTxnsTab,
    ),

}


class InteractionTopLevelWindow(customtkinter.CTkToplevel):
    def __init__(
            self,
            parent,
            action: dict = None,
            on_action_save: Callable[[Union[dict, None]], None] = None,
            title: str = "New action"
    ):
        super().__init__()

        self.master: ActionsFrame = parent
        self.action = action
        self.task = action["task_config"] if action else None
        self.on_action_save = on_action_save

        self.title(title)

        self.after(10, self.focus_force)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)

        self.parent = parent

        self.current_tab_name = None
        self.current_tab = None

        self.chose_module_frame = ChoseModuleFrame(
            master=self,
            action=action
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
        self.tabview.grid_rowconfigure(0, weight=1)

        if self.action:
            self.set_edit_tab()
        else:
            self.set_default_tab()

        self.confirm_button = customtkinter.CTkButton(
            self,
            text="Save",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=100,
            height=35,
            command=self.confirm_button_event
        )
        self.confirm_button.grid(
            row=2,
            column=0,
            padx=40,
            pady=(0, 20),
            sticky="w"
        )

        self.after(10, self.focus_force)

    def set_new_tab(
            self,
            tab_name: str
    ):
        if self.current_tab_name is not None:
            self.tabview.delete(self.current_tab_name)

        self.tabview.add(tab_name)
        self.tabview.set(tab_name)

        tab: Tab = TABS[enums.TabName(tab_name)]
        self.current_tab = tab.tab(
            self.tabview,
            tab_name,
            self.task
        )
        self.current_tab_name = tab_name
        self.chose_module_frame.float_spinbox.max_value = tab.spinbox_max_value
        self.chose_module_frame.float_spinbox.entry.configure(textvariable=Variable(value=1))

    def set_edit_tab(self):
        tab_name = self.action["tab_name"]
        self.tabview.add(tab_name.title())
        self.tabview.set(tab_name.title())
        self.current_tab = TABS[enums.TabName(tab_name)].tab(
            self.tabview,
            tab_name.title(),
            self.task
        )
        self.current_tab_name = tab_name
        self.chose_module_frame.float_spinbox.entry.configure(textvariable=Variable(value=self.action["repeats"]))

    def set_default_tab(self):
        tab_name = self.chose_module_frame.modules_option_menu.get()
        self.tabview.add(tab_name.title())
        self.tabview.set(tab_name.title())
        self.current_tab = modules.SwapTab(
            self.tabview,
            tab_name
        )
        self.current_tab_name = tab_name
        self.chose_module_frame.float_spinbox.max_value = 100
        self.chose_module_frame.float_spinbox.entry.configure(textvariable=Variable(value=1))

    def get_repeats_amount(self) -> Union[int, None]:
        try:
            repeats = int(self.chose_module_frame.float_spinbox.get())
            if repeats < 1:
                return None
            return repeats

        except ValueError:
            return None

    def confirm_button_event(self):
        if self.master.is_running:
            tkinter.messagebox.showerror("Error", "You can't edit action while it's running")
            return

        current_tab = self.current_tab
        if current_tab is None:
            return

        config_data = current_tab.build_config_data()
        if config_data is None:
            return

        if self.action:
            config_data.task_id = self.action["task_config"].task_id

        repeats = self.get_repeats_amount()
        if repeats is None:
            tkinter.messagebox.showerror(
                title="Error",
                message="Repeats amount must be a positive integer"
            )
            return

        self.on_action_save(
            {
                "task_config": config_data,
                "repeats": repeats,
                "tab_name": self.current_tab_name
            }
        )
        if self.action:
            self.master.button_actions_frame.close_edit_action_window()


class ChoseModuleFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            action: dict = None,
    ):
        super().__init__(master=master)
        self.master = master
        self.action = action

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
            values=self.tab_names,
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

        self.float_spinbox = FloatSpinbox(master=self, max_value=100)
        self.float_spinbox.grid(
            row=1,
            column=1,
            padx=20,
            pady=(5, 20),
            sticky="w"
        )

    @property
    def tab_names(self) -> list:
        if self.action:
            values = [self.action["tab_name"]]
        else:
            tab: enums.TabName
            values = [tab.value for tab in enums.TabName]

        return values

