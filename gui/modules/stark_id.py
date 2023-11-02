from src.schemas import tasks
from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.objects import CTkCustomTextBox


class StarkIdMintTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.IdentityMintTask = None

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
            task=task,
        )

        text_box_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "ew"
        }

        text = f"- Module mint's free StarkID with random unused ID.\n\n"

        self.info_textbox = CTkCustomTextBox(
            master=self.tabview.tab(tab_name),
            grid=text_box_grid,
            text=text,
        )

    def build_config_data(self):
        return tasks.IdentityMintTask(
            max_fee=self.txn_settings_frame.max_fee_entry.get(),
        )
