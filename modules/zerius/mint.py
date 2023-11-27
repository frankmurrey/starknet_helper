from typing import Union
from typing import TYPE_CHECKING

from loguru import logger
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account

from modules.base import ModuleBase
from contracts.zerius.main import ZeriusContracts
from contracts.tokens.main import Tokens
from src.schemas.action_models import ModuleExecutionResult, TransactionPayloadData

if TYPE_CHECKING:
    from src.schemas.tasks.zerius import ZeriusMintTask
    from src.schemas.wallet_data import WalletData


class ZeriusMint(ModuleBase):
    task: 'ZeriusMintTask'
    account: Account
    reff_address: str = "0x062d04705B96734eba8622667E9Bc8fec78C77e4c5878B2c72eA84702C17db3b"

    def __init__(
            self,
            account,
            task: 'ZeriusMintTask',
            wallet_data: 'WalletData',
    ):
        super().__init__(
            account=account,
            task=task,
            wallet_data=wallet_data,
        )
        self.task = task
        self.account = account

        self.zerius_contracts = ZeriusContracts()

    async def get_fee_and_token_uri(self, contract: Contract) -> Union[tuple[int, int], None]:
        """
        Get the fee and token uri for the mint transaction.
        :param contract:
        :return:
        """
        try:
            mint_fee_wei = await contract.functions['getMintFee'].call()
            token_uri = await contract.functions['getNextMintId'].call()

            return mint_fee_wei[0], token_uri[0]

        except Exception as e:
            self.log_error(f"Failed to get fee and token uri: {e}")
            return None

    async def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build the transaction payload data for the swap type transaction.
        :return:
        """
        router_contract = await Contract.from_address(
            address=self.zerius_contracts.router_address,
            provider=self.account
        )

        mint_data = await self.get_fee_and_token_uri(contract=router_contract)
        if mint_data is None:
            self.log_error(f"Failed to get fee and token uri")
            return None

        mint_fee_wei, token_uri = mint_data

        eth_address = Tokens().get_by_name('eth').contract_address

        approve_call = self.build_token_approve_call(
            token_addr=eth_address,
            amount_wei=mint_fee_wei,
            spender=hex(router_contract.address)
        )

        func = 'mint'
        call_data = [token_uri]
        if self.task.use_reff:
            func = 'mintWithReferrer'
            call_data.append(self.i16(self.reff_address))

        mint_call = self.build_call(
            to_addr=router_contract.address,
            func_name=func,
            call_data=call_data
        )

        calls = [approve_call, mint_call]

        return TransactionPayloadData(
            calls=calls,
            amount_x_decimals=mint_fee_wei / 10 ** 18,
            amount_y_decimals=token_uri
        )

    async def send_txn(self) -> ModuleExecutionResult:
        """
        Sends transaction.
        :return:
        """
        txn_payload_data = await self.build_txn_payload_data()
        if txn_payload_data is None:
            self.log_error(f"Failed to build txn payload data")
            return self.module_execution_result

        txn_info_message = f"Mint NFT (Zerius). Mint fee: {txn_payload_data.amount_x_decimals} ETH, " \
                           f"Token ID: {int(txn_payload_data.amount_y_decimals)}."

        txn_status = await self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            calls=txn_payload_data.calls,
            txn_info_message=txn_info_message
        )

        return txn_status
