

class TokenBase:
    def __init__(self,
                 symbol: str,
                 contract_address: str,
                 is_jedi_available: bool = None,
                 is_my_swap_available: bool = None,
                 abi: str = None):
        self.symbol = symbol
        self.contract_address = contract_address
        self.abi = abi
        self.is_jedi_available = is_jedi_available
        self.is_my_swap_available = is_my_swap_available
