import os
import subprocess
import functools


@functools.cache
def is_windows() -> bool:
    return os.name == "nt"


@functools.cache
def is_linux() -> bool:
    return os.name == "posix"


@functools.cache
def mingw_installed() -> bool:
    try:

        exec_result = (
            subprocess.check_output(["gcc", "--version"])
            .decode("utf-8")
            .lower()
        )

        return "mingw" in exec_result

    except FileNotFoundError:
        return False