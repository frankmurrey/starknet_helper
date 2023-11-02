from contracts.base import TokenBase

from utils.file_manager import FileManager

from src.paths import TempFiles
from src.paths import TOKENS_ABI_DIR

from loguru import logger


class Tokens:
    def __init__(self):
        self.all_tokens_data_from_file = FileManager().read_data_from_json_file(TempFiles().TOKENS_JSON_FILE)
        self.all_tokens = [*self.default_tokens, *self.custom_tokens]

    def _get_token_abi(
            self,
            symbol: str
    ):
        return FileManager.read_abi_from_file(f"{TOKENS_ABI_DIR}\\{symbol.lower()}.abi")

    def _get_tokens_obj(self, tokens_data: list):
        try:
            return [TokenBase(**token_data) for token_data in tokens_data]

        except Exception as e:
            logger.error(f"Error while creating token objects: {e}")
            exit(1)

    @property
    def general_tokens(self) -> list:
        symbols = ["eth", "usdt", "usdc", "dai"]
        return [token for token in self.all_tokens if token.symbol in symbols]

    @property
    def default_tokens(self) -> list:
        try:
            all_obj = []
            tokens = self.all_tokens_data_from_file[0]["default"]
            tokens_obj = self._get_tokens_obj(tokens)
            for token_obj in tokens_obj:
                token_abi = self._get_token_abi(symbol=token_obj.symbol)
                token_obj.abi = token_abi
                all_obj.append(token_obj)

            return all_obj

        except Exception as e:
            logger.error(f"Error while creating default token objects: {e}")
            exit(1)

    @property
    def custom_tokens(self) -> list:
        try:
            all_obj = []
            tokens = self.all_tokens_data_from_file[0]["custom"]
            tokens_obj = self._get_tokens_obj(tokens)
            for token_obj in tokens_obj:
                token_abi = self._get_token_abi(symbol=token_obj.symbol)
                token_obj.abi = token_abi
                all_obj.append(token_obj)

            return all_obj

        except Exception as e:
                logger.error(f"Error while creating custom token objects: {e}")
                exit(1)

    def update_tokens_data(self):
        self.all_tokens_data_from_file = FileManager().read_data_from_json_file(TempFiles().TOKENS_JSON_FILE)
        self.all_tokens = [*self.default_tokens, *self.custom_tokens]

    def get_by_name(self, name_query):
        for token in self.all_tokens:
            if token.symbol.lower() == name_query.lower():
                return token
        logger.error(f"Token {name_query} not found")
        return None

    def get_cg_id_by_name(self, name_query):
        for token in self.all_tokens:
            if token.symbol.lower() == name_query.lower():
                return token.coin_gecko_id
        logger.error(f"Token {name_query} not found")
        return None

    def get_tokens_by_protocol(
            self,
            protocol: str
    ) -> list:
        tokens = []
        for token in self.all_tokens:
            if protocol.lower() in token.available_protocol:
                tokens.append(token)
        return tokens
