import os
import subprocess


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


def decode_wallet_version(version: int) -> str:
    """
    Converts a binary version number to a human-readable string.

    Args:
    version (int): The version number to be converted.

    Returns:
    str: The human-readable version number.
    """
    version_bytes = version.to_bytes(31, byteorder="big")

    char_list = [chr(i) for i in version_bytes]

    version_string = "".join(char_list)

    final_version = version_string.lstrip("\x00")

    return final_version


if __name__ == '__main__':
    print(mingw_installed())
