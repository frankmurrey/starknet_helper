from src.schemas.tasks.identity import IdentityMintTask
from gui.modules.txn_settings_frame import TxnSettingFrame


class StarkIdMintTab:
    def __init__(
            self,
            tabview,
            tab_name
    ):
        self.tabview = tabview

        self.tab_name = tab_name

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid={
                "row": 0,
                "column": 0,
                "padx": 20,
                "pady": 20,
                "sticky": "nsew"
            }
        )

    def build_config_data(self):
        return IdentityMintTask(
            max_fee=self.txn_settings_frame.max_fee_entry.get(),
        )