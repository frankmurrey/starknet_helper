from utils.orbiter_utils import get_available_tokens_for_chain


class TokenBase:
    def __init__(
            self,
            symbol: str,
            contract_address: str,
            coin_gecko_id: str = None,
            available_protocols: list = None,
            abi: str = None
    ):
        if available_protocols is None:
            available_protocols = []

        self.symbol = symbol
        self.available_protocol = available_protocols
        self.contract_address = contract_address
        self.abi = abi

        self.coin_gecko_id = coin_gecko_id


class ChainBase:
    def __init__(
            self,
            name: str,
            orbiter_id: int,
            supported_tokens: list = None
    ):
        self.name = name
        self.orbiter_id = orbiter_id
        self.supported_tokens = supported_tokens
        self.orbiter_supported_tokens = get_available_tokens_for_chain(chain_id=self.orbiter_id)
