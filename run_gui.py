from gui.main_window.main import run_gui
from utils.system import is_windows
from utils.system import mingw_installed
from loguru import logger


if __name__ == '__main__':
    if is_windows() and not mingw_installed():
        logger.error("MinGW is not installed, please install it and try again")
        logger.error("https://starknetpy.readthedocs.io/en/latest/installation.html#windows")
        exit(1)

    run_gui()
