import os
import json


class FileManager:
    def __init__(self):
        pass

    @staticmethod
    def read_abi_from_file(file_path: str):
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r") as f:
                return json.loads(f.read())
        except Exception as e:
            return None

    @staticmethod
    def read_data_from_json_file(file_path):
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r") as file:
                data = json.load(file)
                return data

        except Exception as e:
            return None

