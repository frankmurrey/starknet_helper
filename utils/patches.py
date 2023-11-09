import asyncio

from utils.system import is_windows


def asyncio_win_patch():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def patch_windows():
    assert is_windows()

    asyncio_win_patch()
