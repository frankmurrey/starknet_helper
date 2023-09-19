import config

from enum import Enum

from colorama import Fore, Back, Style

from src.schemas.tasks.base import TaskBase
from modules.base import ModuleBase
from utlis.repr.misc import Symbol
from utlis.repr.misc import AsciiPrints
from utlis.repr.misc import COLOR_LENGTH
from utlis.repr.misc import MODULE_NAME_MAX_LENGTH


class Colors:
    BORDER = Fore.LIGHTBLUE_EX

    MODULE_NAME = Fore.LIGHTMAGENTA_EX
    MODULE_HEADER_TEXT = Fore.LIGHTCYAN_EX

    CONFIG_KEY_COLOR = Fore.LIGHTMAGENTA_EX
    CONFIG_VALUE_COLOR = Fore.LIGHTCYAN_EX


def get_border_top(width: int) -> str:
    repr_string = Colors.BORDER

    repr_string += Symbol.left_top + Symbol.top * (width - 2) + Symbol.right_top

    repr_string += Fore.RESET

    return repr_string


def get_border_bottom(key_width: int, value_width: int) -> str:
    repr_string = Colors.BORDER

    repr_string += Symbol.left_bottom
    repr_string += Symbol.bottom * (key_width + 3)
    repr_string += Symbol.bottom_middle
    repr_string += Symbol.bottom * (value_width + 3)
    repr_string += Symbol.right_bottom

    repr_string += Fore.RESET

    return repr_string


def get_border_middle(key_width: int, value_width: int) -> str:
    repr_string = Colors.BORDER

    repr_string += Symbol.left_middle + Symbol.top * (key_width + 3) + Symbol.top_middle + Symbol.top * (value_width + 3) + Symbol.right_middle

    repr_string += Fore.RESET

    return repr_string


def get_module_name_header(module_name: str, width: int) -> str:

    if len(module_name) > MODULE_NAME_MAX_LENGTH:
        strip_size = int(MODULE_NAME_MAX_LENGTH / 2)
        module_name = f"{module_name[:strip_size - 1]}...{module_name[-strip_size+3:]}"

    module_name = f"{Colors.MODULE_NAME}{module_name.capitalize()}"

    header_text = f"{module_name}"
    header_text += f"{Colors.MODULE_HEADER_TEXT}'s module config"
    header_text += f"{Fore.RESET}"

    space_width = width - 4 + 3 * COLOR_LENGTH

    repr_string = Colors.BORDER
    repr_string += Symbol.left
    repr_string += Fore.RESET

    repr_string += f" {header_text:^{space_width}} "

    repr_string += Colors.BORDER
    repr_string += Symbol.left
    repr_string += Fore.RESET

    return repr_string


def get_max_width(max_key_width: int, max_value_width: int) -> int:
    return 2 + max_key_width + 5 + max_value_width + 2


def print_module_config(task: TaskBase):

    repr_strings = []

    task_dict = task.dict(exclude={"module_name", "module"})

    max_key_width = max(len(key) for key in task_dict.keys())
    max_value_width = max(len(str(value)) for value in task_dict.values())
    max_width = get_max_width(max_key_width, max_value_width)

    for key, value in task_dict.items():

        key_width = max_key_width
        value_width = max_value_width

        key = key.title().replace("_", " ")
        key = f"{Colors.CONFIG_KEY_COLOR}{key}{Fore.RESET}"
        key_width = key_width + 2 * COLOR_LENGTH

        if issubclass(value.__class__, Enum):
            value = str(value.value).upper()

        if isinstance(value, bool):
            value_width = value_width + 2 * COLOR_LENGTH
            value = (f"{Fore.GREEN}+" if value else f"{Fore.RED}-") + Fore.RESET

        else:
            value_width += 2 * COLOR_LENGTH
            value = f"{Colors.CONFIG_VALUE_COLOR}{value}{Fore.RESET}"

        repr_string = Colors.BORDER
        repr_string += Symbol.left
        repr_string += Fore.RESET

        repr_string += f" {key:>{key_width + 1}} "

        repr_string += Colors.BORDER
        repr_string += Symbol.center
        repr_string += Fore.RESET

        repr_string += f" {value:<{value_width + 1}} "

        repr_string += Colors.BORDER
        repr_string += Symbol.right
        repr_string += Fore.RESET

        repr_strings.append(repr_string)

    repr_strings.insert(0, get_module_name_header(task.module_name, max_width))
    repr_strings.insert(0, get_border_top(max_width))
    repr_strings.insert(2, get_border_middle(key_width=max_key_width, value_width=max_value_width))
    repr_strings.append(get_border_bottom(key_width=max_key_width, value_width=max_value_width))

    repr_strings.insert(0, Style.BRIGHT)
    repr_strings.append(Style.BRIGHT)

    print(f"{Fore.LIGHTMAGENTA_EX}{AsciiPrints.pre_config_1}{Fore.RESET}")
    print(*repr_strings, sep="\n")
    print(f"{Fore.LIGHTMAGENTA_EX}Made by Frank Murrey - https://github.com/frankmurrey{Fore.RESET}")
    print(f"{Fore.LIGHTMAGENTA_EX}Starting in {config.DEFAULT_DELAY_SEC} sec...{Fore.RESET}\n")
