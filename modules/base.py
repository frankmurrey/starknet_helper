import asyncio
import random
import json

from typing import Union

from utlis.key_manager.key_manager import (get_key_pair_from_pk,
                                           get_argent_addr_from_private_key,
                                           get_braavos_addr_from_private_key)

from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.models.transaction import (DeployAccount,
                                                Invoke)
from starknet_py.net.account.account_deployment_result import AccountDeploymentResult
from starknet_py.net.client_models import (
    EstimatedFee
)
from starknet_py.contract import Contract
from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call
from starknet_py.hash.selector import get_selector_from_name


from loguru import logger


class StarkBase:
    ETH_ADDRESS_MAINNET = '0x049D36570D4E46F48E99674BD3FCC84644DDD6B96F7C741B1562B82F9E004DC7'

    def __init__(self,
                 client: FullNodeClient,
                 ):
        self.client = client
        self.chain_id = StarknetChainId.MAINNET

    def i16(self,
            hex_d: str):
        return  int(hex_d, 16)

    def get_random_amount_out_of_token(self,
                                       min_amount,
                                       max_amount,
                                       decimals: int) -> int:
        random_amount = random.uniform(min_amount, max_amount)
        return int(random_amount * 10 ** decimals)

    def get_account_argent(self,
                           private_key: str) -> Account:
        key_pair = get_key_pair_from_pk(private_key)
        raw_address = get_argent_addr_from_private_key(private_key)

        return Account(address=raw_address,
                       client=self.client,
                       key_pair=key_pair,
                       chain=self.chain_id)

    def get_account_braavos(self,
                            private_key: str) -> Account:
        key_pair = get_key_pair_from_pk(private_key)
        raw_address = get_braavos_addr_from_private_key(private_key)

        return Account(address=raw_address,
                       client=self.client,
                       key_pair=key_pair,
                       chain=self.chain_id)

    def get_contract(self,
                     address,
                     abi,
                     provider):
        return Contract(
            address=address,
            abi=abi,
            provider=provider
        )

    async def get_token_decimals(self,
                                 contract_address,
                                 abi,
                                 provider):
        token_contract = self.get_contract(address=contract_address,
                                           abi=abi,
                                           provider=provider)
        decimals = await token_contract.functions['decimals'].call()
        return decimals.decimals

    async def check_token_allowance_for_spender(self,
                                                token_address,
                                                token_abi,
                                                wallet_address,
                                                spender_address,
                                                provider):
        token_contract = self.get_contract(address=token_address,
                                           abi=token_abi,
                                           provider=provider)
        allowance = await token_contract.functions['allowance'].call(
            wallet_address,
            spender_address
        )
        return allowance.remaining

    def build_call(self,
                   to_addr: int,
                   func_name: str,
                   call_data: list
                   ):
        return Call(
            to_addr=to_addr,
            selector=get_selector_from_name(func_name),
            calldata=call_data
        )

    def build_token_approve_call(self,
                                 token_addr: str,
                                 amount_wei: int,
                                 spender: str):
        return Call(
            to_addr=self.i16(token_addr),
            selector=get_selector_from_name('approve'),
            calldata=[self.i16(spender),
                      amount_wei,
                      0]
        )

    async def build_approval_txn(self,
                                 token_address,
                                 token_abi,
                                 provider,
                                 spender,
                                 amount_wei,
                                 max_fee):
        token_contract = self.get_contract(address=token_address,
                                           abi=token_abi,
                                           provider=provider)
        prepared_call = token_contract.functions['approve'].prepare(
            spender,
            amount_wei,
            max_fee=max_fee
        )

        return prepared_call

    async def get_eth_balance(self,
                              account: Account):
        return await account.get_balance(token_address=self.ETH_ADDRESS_MAINNET)

    async def get_token_balance(self,
                                account: Account,
                                token_address: int):
        return await account.get_balance(token_address=token_address)

    async def get_nonce(self,
                        account: Account):
        try:
            return await account.get_nonce()
        except ClientError:
            return 0

    async def get_estimated_transaction_fee(self,
                                            account: Account,
                                            transaction):
        try:
            estimate = await account.client.estimate_fee(transaction)
            return estimate.overall_fee
        except ClientError as error:
            print(error.code, error.message)
            return None

    async def wait_for_tx_receipt(self,
                                  tx_hash: int,
                                  time_out_sec: int):
        try:
            return await self.client.wait_for_tx(tx_hash=tx_hash,
                                                 check_interval=5,
                                                 retries=(time_out_sec // 2) + 1)
        except Exception as ex:
            logger.error(f"Error while waiting for txn receipt: {ex}")
            return False

    async def deploy_account_argent(self,
                                    private_key: str) -> Union[AccountDeploymentResult, None]:
        key_pair = get_key_pair_from_pk(private_key)
        raw_address = get_argent_addr_from_private_key(private_key)
        class_hash = 0x025ec026985a3bf9d0cc1fe17326b245dfdc3ff89b8fde106542a3ea56c5a918
        account_initialize_call_data = [key_pair.public_key, 0]

        call_data = [
            0x33434ad846cdd5f23eb73ff09fe6fddd568284a0fb7d1be20ee482f044dabe2,
            0x79dc0da7c54b95f10aa182ad0a46400db63156920adb65eca2654c0945a463,
            len(account_initialize_call_data),
            *account_initialize_call_data
        ]

        account = self.get_account_argent(private_key=private_key)
        nonce = await self.get_nonce(account=account)

        deploy_txn = DeployAccount(
            class_hash=class_hash,
            contract_address_salt=key_pair.public_key,
            constructor_calldata=call_data,
            version=1,
            max_fee=int(1e15),
            nonce=nonce,
            signature=[])

        estimate_fee = await self.get_estimated_transaction_fee(account=account,
                                                                transaction=deploy_txn)

        if estimate_fee is None:
            return None

        deploy_result = await account.deploy_account(
            address=raw_address,
            class_hash=class_hash,
            salt=key_pair.public_key,
            key_pair=key_pair,
            client=self.client,
            chain=self.chain_id,
            constructor_calldata=call_data,
            max_fee=estimate_fee
        )

        return deploy_result

    async def deploy_account_braavos(self,
                                     private_key: str):
        key_pair = get_key_pair_from_pk(private_key)
        raw_address = get_braavos_addr_from_private_key(private_key)
        class_hash = 0x03131fa018d520a037686ce3efddeab8f28895662f019ca3ca18a626650f7d1e

        account_initialize_call_data = [key_pair.public_key]
        call_data = [
            0x5aa23d5bb71ddaa783da7ea79d405315bafa7cf0387a74f4593578c3e9e6570,
            0x2dd76e7ad84dbed81c314ffe5e7a7cacfb8f4836f01af4e913f275f89a3de1a,
            len(account_initialize_call_data),
            *account_initialize_call_data
        ]

        account = self.get_account_braavos(private_key=private_key)
        nonce = await self.get_nonce(account=account)

        deploy_txn = DeployAccount(
            class_hash=class_hash,
            contract_address_salt=key_pair.public_key,
            constructor_calldata=call_data,
            version=1,
            max_fee=int(1e15),
            nonce=nonce,
            signature=[])

        estimate_fee = await self.get_estimated_transaction_fee(account=account,
                                                                transaction=deploy_txn)

        if estimate_fee is None:
            return None

        deploy_result = await account.deploy_account(
            address=raw_address,
            class_hash=class_hash,
            salt=key_pair.public_key,
            key_pair=key_pair,
            client=self.client,
            chain=self.chain_id,
            constructor_calldata=call_data,
            max_fee=estimate_fee
        )

        return deploy_result

    async def simulate_and_send_transfer_type_transaction(self,
                                                          account: Account,
                                                          config,
                                                          calls: list,
                                                          txn_info_message: str):
        logger.warning(f"Action: {txn_info_message}")

        signed_invoke_transaction = await account.sign_invoke_transaction(calls=calls,
                                                                          max_fee=0)

        estimate_transaction = await self.get_estimated_transaction_fee(account=account,
                                                                        transaction=signed_invoke_transaction)
        if estimate_transaction is None:
            logger.error(f"Transaction estimation failed. Aborting transaction.")
            return False

        estimate_gas_decimals = estimate_transaction / 10 ** 18
        wallet_eth_balance = await self.get_eth_balance(account=account)
        wallet_eth_balance_decimals = wallet_eth_balance / 10 ** 18

        if wallet_eth_balance < estimate_transaction:
            logger.error(f"Insufficient ETH balance for txn fees (balance: {wallet_eth_balance_decimals}, "
                         f"need {estimate_gas_decimals} ETH). Aborting transaction.")
            return False

        logger.success(f"Transaction estimation success, overall fee: "
                       f"{estimate_gas_decimals} ETH.")

        if config.forced_gas_limit is True:
            gas_limit = int(config.gas_limit)
        else:
            gas_limit = int(estimate_transaction * 1.4)

        if config.test_mode is True:
            logger.debug(f"Test mode enabled. Skipping transaction")
            return False

        response = await account.execute(calls=calls, max_fee=gas_limit)

        txn_hash = response.transaction_hash

        if config.wait_for_receipt is True:
            logger.debug(f"Txn sent. Waiting for receipt (Timeout in {config.txn_wait_timeout_sec}s)."
                         f" Txn Hash: {hex(txn_hash)}")

            txn_receipt = await self.wait_for_tx_receipt(tx_hash=txn_hash,
                                                         time_out_sec=config.txn_wait_timeout_sec)
            if txn_receipt is False:
                return False

            logger.success(f"Txn success, status: {txn_receipt.status} "
                           f"(Actual fee: {txn_receipt.actual_fee / 10 ** 18}. "
                           f"Txn Hash: {hex(txn_hash)})")

            return True

        else:
            logger.success(f"Txn sent. Txn Hash: {hex(txn_hash)}")
            return True
