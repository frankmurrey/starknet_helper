import re

from typing import Union


def detect_separator(
        filename: str,
        possible_delimiters: list[str]
) -> Union[str, None]:
    with open(filename, 'r', newline='') as file:
        first_line = file.readline()
        for delimiter in possible_delimiters:
            if re.search(f"[{delimiter}]", first_line):
                return delimiter

    return None


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
