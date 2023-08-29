import pandas as pd
from loguru import logger


def write_balance_data_to_xlsx(path,
                               data: list[dict],
                               coin_option):

    datapd = {
        "Wallet Address": [],
        "Balance": [],
        "Coin": []
    }

    for wallet in data:
        for addr, balance in wallet.items():
            datapd["Wallet Address"].append(addr)
            datapd["Balance"].append(balance)
            datapd["Coin"].append(coin_option)

    df = pd.DataFrame(datapd)
    try:
        df.to_excel(path, index=False)

        logger.warning(f"Balance data saved to {path}")
    except Exception as e:
        logger.error(f"Error while saving balance data to {path}: {e}")