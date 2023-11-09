from src.schemas import tasks
from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.objects import CTkCustomTextBox


class DmailSendMailTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.DmailSendMailTask = None
    ):
        self.tabview = tabview

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid={
                "row": 0,
                "column": 0,
                "padx": 20,
                "pady": 20,
                "sticky": "nsew"
            },
            task=task
        )

        text_box_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "ew"
        }

        text = f"- This module only sends 'Dmail confirmation txn'\n\n" \
               f"- If you want to send real mail letter, you must do it through the website\n\n" \
               f"- Recipient address and theme generates automatically (truthful attributes)\n\n"

        self.info_textbox = CTkCustomTextBox(
            master=self.tabview.tab(tab_name),
            grid=text_box_grid,
            text=text,
            height=200,
        )

    def build_config_data(self):
        return tasks.DmailSendMailTask(
            max_fee=self.txn_settings_frame.max_fee_entry.get(),
            forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
        )
