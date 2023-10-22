from typing import Union

from utils.file_manager import FileManager
from src import paths
from src.schemas.data_models import OrbiterChainData


def get_orbiter_bridge_data_by_chain(chain_id: int) -> Union[dict, None]:
    bridge_data = FileManager.read_data_from_json_file(paths.OrbiterDir.BRIDGE_DATA_FILE)
    chain_id = str(chain_id)

    for key, value in bridge_data.items():
        dst_id = key.split("-")[1]
        if int(dst_id) == int(chain_id[2:]):
            return value

    return None


def get_orbiter_bridge_data_by_token(
        chain_id: int,
        token_symbol: str
) -> Union[OrbiterChainData, None]:

    chain_data = get_orbiter_bridge_data_by_chain(chain_id)
    if chain_data is None:
        return None

    for key, value in chain_data.items():
        symbol = key.split("-")[1]
        if symbol.lower() == token_symbol.lower():
            return OrbiterChainData(**value)

    return None


def get_available_tokens_for_chain(chain_id: int):
    chain_data = get_orbiter_bridge_data_by_chain(chain_id)
    if chain_data is None:
        return None

    return [key.split("-")[1] for key in chain_data.keys()]


