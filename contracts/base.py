

class TokenBase:
    def __init__(self,
                 symbol: str,
                 contract_address: str,
                 coin_gecko_id: str = None,
                 available_protocols: list = None,
                 abi: str = None):
        if available_protocols is None:
            available_protocols = []

        self.symbol = symbol
        self.available_protocol = available_protocols
        self.contract_address = contract_address
        self.abi = abi

        self.coin_gecko_id = coin_gecko_id
