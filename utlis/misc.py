import os
import subprocess


def mingw_installed() -> bool:
    try:

        exec_result = (
            subprocess.check_output(["gascc", "--version"])
            .decode("utf-8")
            .lower()
        )

        return "mingw" in exec_result

    except FileNotFoundError:
        return False


if __name__ == '__main__':
    print(mingw_installed())
