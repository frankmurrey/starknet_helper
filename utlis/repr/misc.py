from colorama import Fore, Back, Style


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


class ColorLength:
    BLACK = len(Fore.BLACK)
    RED = len(Fore.RED)
    GREEN = len(Fore.GREEN)
    YELLOW = len(Fore.YELLOW)
    BLUE = len(Fore.BLUE)
    MAGENTA = len(Fore.MAGENTA)
    CYAN = len(Fore.CYAN)
    WHITE = len(Fore.WHITE)
    RESET = len(Fore.RESET)
