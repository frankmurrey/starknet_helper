from gui.main_window.main import run_gui
from utils.misc import mingw_installed
from loguru import logger


if __name__ == '__main__':
    if mingw_installed() is False:
        logger.error("MinGW is not installed, please install it and try again")
        logger.error("https://starknetpy.readthedocs.io/en/latest/installation.html#windows")
        exit(1)

    run_gui()
