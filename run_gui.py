from loguru import logger

from src.templates.templates import Templates
from utlis.misc import mingw_installed


def on_startup():
    # Templates().create_not_found_temp_files()

    if not mingw_installed():
        logger.critical("MinGW in not installed.")
        exit(1)


if __name__ == '__main__':
    on_startup()
