from colorama import Fore, Back, Style


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


class AsciiPrints:
    pre_config_1 = '''
     ______   __  ___                          
    / ____/  /  |/  __  _______________  __  __
   / /_     / /|_/ / / / / ___/ ___/ _ \/ / / /
  / __/    / /  / / /_/ / /  / /  /  __/ /_/ / 
 /_/      /_/  /_/\__,_/_/  /_/   \___/\__, /  
                                       /___/   '''
