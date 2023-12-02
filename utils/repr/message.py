from datetime import datetime, timedelta
from typing import Union
from typing import TYPE_CHECKING

from colorama import Fore

from utils.repr.color import Color
from utils.repr.private_key import blur_private_key

if TYPE_CHECKING:
    from src.schemas.wallet_data import WalletData


def logo() -> str:
    return '''
     ______   __  ___                          
    / ____/  /  |/  /_  _______________  __  __
   / /_     / /|_/ / / / / ___/ ___/ _ \/ / / /
  / __/    / /  / / /_/ / /  / /  /  __/ /_/ / 
 /_/      /_/  /_/\__,_/_/  /_/   \___/\__, /  
                                       /___/   '''


def logo_message() -> str:
    return f"{Fore.LIGHTMAGENTA_EX}{logo()}{Fore.RESET}\n"


def task_exec_sleep_message(
        time_to_sleep: Union[int, float],
) -> str:
    continue_datetime = datetime.now() + timedelta(seconds=time_to_sleep)
    return (
        f"Time to sleep for {int(time_to_sleep)} seconds..."
        f" Continue at {continue_datetime.strftime('%H:%M:%S')}"
    )


def wallet_execution_message(
        wallet: "WalletData",
) -> str:
    msg = (
        f"\n"
        f"{Color.BORDER}[{Fore.RESET}"
        f"{wallet.index + 1}"
        f"{Color.BORDER}]{Fore.RESET} "
        f"{Color.CONFIG_KEY_COLOR}{wallet.name}{Fore.RESET}"
        f" - "
        f"{Color.CONFIG_VALUE_COLOR}{wallet.address}{Fore.RESET}"
    )
    msg += "\n"
    msg += (
        f"{Color.CONFIG_KEY_COLOR}PK{Fore.RESET}"
        f" - "
        f"{Color.CONFIG_VALUE_COLOR}{blur_private_key(wallet.private_key)}{Fore.RESET}"
    )

    return msg
