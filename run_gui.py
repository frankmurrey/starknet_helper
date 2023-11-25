from loguru import logger

from utils.args import get_args
from utils import patches
from utils.system import is_windows
from utils.system import mingw_installed
from utils.system import get_missed_requirements


if __name__ == '__main__':
    args = get_args()

    if not args.no_check_req:
        missed_requirements = get_missed_requirements()

        if len(missed_requirements) > 0:
            logger.error(f"Missing requirements: {', '.join(missed_requirements)}")
            logger.error("Please run \"pip install -r req.txt\"")
            exit(1)

        if is_windows() and not mingw_installed():
            logger.error("MinGW is not installed, please install it and try again")
            logger.error("https://starknetpy.readthedocs.io/en/latest/installation.html#windows")
            exit(1)

    if is_windows():
        patches.patch_windows()

    from src.storage import Storage
    storage = Storage()
    storage.update_app_config_values(debug=args.debug)

    from gui.main_window.main import run_gui
    run_gui()
