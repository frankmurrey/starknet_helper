from enum import Enum

from colorama import Fore, Back, Style

from src.schemas.configs.base import CommonSettingsBase
from utlis.repr.misc import Symbol
from utlis.repr.misc import ColorLength as CL


def get_border_top(width: int) -> str:
    return Symbol.left_top + Symbol.top * (width - 2) + Symbol.right_top


def get_border_bottom(key_width: int, value_width: int) -> str:
    repr_string = Symbol.left_bottom
    repr_string += Symbol.bottom * (key_width + 3)
    repr_string += Symbol.bottom_middle
    repr_string += Symbol.bottom * (value_width + 3)
    repr_string += Symbol.right_bottom
    return repr_string


def get_border_middle(key_width: int, value_width: int) -> str:
    return Symbol.left_middle + Symbol.top * (key_width + 3) + Symbol.top_middle + Symbol.top * (value_width + 3) + Symbol.right_middle


def get_module_name_header(module_name: str, width: int) -> str:
    module_name = f"{Fore.CYAN}{module_name.capitalize()}{Fore.RESET}"
    header_text = f"{module_name}'s module config"
    space_width = width - 4 + CL.CYAN + CL.RESET
    repr_string = f"{Symbol.left} {header_text:^{space_width}} {Symbol.center}"

    return repr_string


def get_max_width(max_key_width: int, max_value_width: int) -> int:
    return 2 + max_key_width + 5 + max_value_width + 2


def print_module_config(module_config: CommonSettingsBase):

    repr_strings = []

    max_key_width = max(len(key) for key in module_config.model_dump(exclude={"module_name"}).keys())
    max_value_width = max(len(str(value)) for value in module_config.model_dump(exclude={"module_name"}).values())
    max_width = get_max_width(max_key_width, max_value_width)

    for key, value in module_config.model_dump(exclude={"module_name"}).items():
        key_width = max_key_width
        value_width = max_value_width

        key = key.title().replace("_", " ")
        key = f"{Fore.YELLOW}{key}{Fore.RESET}"
        key_width = key_width + CL.YELLOW + CL.RESET

        if isinstance(value, bool):
            value_width = value_width + (CL.GREEN if value else CL.RED) + CL.RESET
            value = (f"{Fore.GREEN}+" if value else f"{Fore.RED}-") + Fore.RESET

        if issubclass(value.__class__, Enum):
            value = str(value.value).upper()
        repr_strings.append(f"{Symbol.left} {key:>{key_width + 1}} {Symbol.center} {value:<{value_width + 1}} {Symbol.right}")

    repr_strings.insert(0, get_module_name_header(module_config.module_name, max_width))
    repr_strings.insert(0, get_border_top(max_width))
    repr_strings.insert(2, get_border_middle(key_width=max_key_width, value_width=max_value_width))
    repr_strings.append(get_border_bottom(key_width=max_key_width, value_width=max_value_width))

    repr_strings.insert(0, Style.BRIGHT)
    repr_strings.append(Style.BRIGHT)

    print("\n".join(repr_strings))


if __name__ == '__main__':
    from src.schemas.configs.jediswap import JediSwapConfigSchema

    cfg_j = JediSwapConfigSchema(
        coin_to_swap='usdt',
        coin_to_receive='usdc',
        min_amount_out=0.5,
        max_amount_out=1,
        slippage=2,
        test_mode=True,
        wait_for_receipt=True,
        txn_wait_timeout_sec=120,
    )

    print_module_config(cfg_j)
