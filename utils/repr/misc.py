from colorama import Fore, Back, Style
from loguru import logger

from src.schemas.wallet_data import WalletData
from utils.repr.private_key import blur_private_key

MODULE_NAME_MAX_LENGTH = 24

COLOR_LENGTH = 5


class Symbol:
    left_top = "╔"
    right_top = "╗"
    left_bottom = "╚"
    right_bottom = "╝"

    left = "║"
    right = "║"
    top = "═"
    bottom = "═"
    center = "║"

    left_middle = "╠"
    right_middle = "╣"
    top_middle = "╦"
    bottom_middle = "╩"


class Colors:
    BORDER = Fore.LIGHTBLUE_EX

    MODULE_NAME = Fore.LIGHTMAGENTA_EX
    MODULE_HEADER_TEXT = Fore.LIGHTCYAN_EX

    CONFIG_KEY_COLOR = Fore.LIGHTMAGENTA_EX
    CONFIG_VALUE_COLOR = Fore.LIGHTCYAN_EX


class AsciiPrints:
    pre_config_1 = '''
     ______   __  ___                          
    / ____/  /  |/  __  _______________  __  __
   / /_     / /|_/ / / / / ___/ ___/ _ \/ / / /
  / __/    / /  / / /_/ / /  / /  /  __/ /_/ / 
 /_/      /_/  /_/\__,_/_/  /_/   \___/\__, /  
                                       /___/   '''


def print_logo():
    print(f"{Fore.LIGHTMAGENTA_EX}{AsciiPrints.pre_config_1}{Fore.RESET}")


def print_wallet_execution(wallet: "WalletData", wallet_index: int):
    print(
        f"\n"
        f"{Colors.BORDER}[{Fore.RESET}"
        f"{wallet_index + 1}"
        f"{Colors.BORDER}]{Fore.RESET} "
        f"{Colors.CONFIG_KEY_COLOR}{wallet.name}{Fore.RESET}"
        f" - "
        f"{Colors.CONFIG_VALUE_COLOR}{wallet.address}{Fore.RESET}"
    )
    print(
        f"{Colors.CONFIG_KEY_COLOR}PK{Fore.RESET}"
        f" - "
        f"{Colors.CONFIG_VALUE_COLOR}{blur_private_key(wallet.private_key)}{Fore.RESET}"
    )


if __name__ == '__main__':
    wallet = WalletData(
        name="Aidar",
        private_key="0xbd910e6b3a04f879602656546b97291ca035cd46a01b812ef6bc66c97f75b477",
    )

    print_wallet_execution(wallet, 3)
