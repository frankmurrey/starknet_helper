from contracts.base import ChainBase


from loguru import logger


class Chains:
    def __init__(self):
        self.all_chains = [
            ChainBase(
                name="Optimism",
                orbiter_id=9007
            ),

            ChainADDBase(
                name="Ethereum",
                orbiter_id=9001
            ),

            ChainBase(
                name="BSC",
                orbiter_id=9015
            ),

            ChainBase(
                name="Polygon",
                orbiter_id=9006
            ),

            ChainBase(
                name="Arbitrum",
                orbiter_id=9002
            ),

            ChainBase(
                name="zkSync Lite",
                orbiter_id=9003
            ),

            ChainBase(
                name="zkSync Era",
                orbiter_id=9016

            ),

            ChainBase(
                name="Polygon zk",
                orbiter_id=9017
            ),

            ChainBase(
                name="Base",
                orbiter_id=9021
            ),

            ChainBase(
                name="Linea",
                orbiter_id=9023
            ),

            ChainBase(
                name="Zora",
                orbiter_id=9030
            ),

        ]

    def get_by_name(self, name_query):
        for chain in self.all_chains:
            if chain.name.lower() == name_query.lower():
                return chain

        logger.error(f"Chain {name_query} not found")

        return None

