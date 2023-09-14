import httpx


def get_eth_mainnet_gas_price(rpc_url: str):
    try:
        client = httpx.Client()
        payload = {"jsonrpc": "2.0",
                   "method": "eth_gasPrice",
                   "params": [],
                   "id": "1"}

        resp = client.post(url=rpc_url, json=payload)

        if resp.status_code != 200:
            return None

        return int(resp.json()['result'], 16) / 1e9

    except Exception as e:
        return None
