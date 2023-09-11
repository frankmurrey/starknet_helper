import unittest

from pydantic import ValidationError

from src.schemas.tasks.base import TaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.swap import SwapTaskBase

from src import enums


class TestTaskBase(unittest.TestCase):

    def test_txn_wait_timeout_sec_not_a_number(self):
        with self.assertRaises(ValidationError) as context:
            TaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                wait_for_receipt=False,
                txn_wait_timeout_sec="not a number",

                min_delay_sec=40,
                max_delay_sec=80,

                test_mode=True,
            )

        self.assertTrue("Txn Wait Timeout should be a float" in str(context.exception))

    def test_txn_wait_timeout_sec_not_positive(self):
        with self.assertRaises(ValidationError) as context:
            TaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                wait_for_receipt=False,
                txn_wait_timeout_sec=-1,

                min_delay_sec=40,
                max_delay_sec=80,

                test_mode=True,
            )

        self.assertTrue("Txn Wait Timeout should be > 0" in str(context.exception))

    def test_min_delay_sec_not_a_number(self):
        with self.assertRaises(ValidationError) as context:
            TaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                wait_for_receipt=False,
                txn_wait_timeout_sec=-1,

                min_delay_sec="not a number",
                max_delay_sec=80,

                test_mode=True,
            )

        self.assertTrue("Min Delay should be a float" in str(context.exception))

    def test_min_delay_sec_not_positive(self):
        with self.assertRaises(ValidationError) as context:
            TaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                wait_for_receipt=False,
                txn_wait_timeout_sec=-1,

                min_delay_sec=-1,
                max_delay_sec=80,

                test_mode=True,
            )

        self.assertTrue("Min Delay should be > 0" in str(context.exception))

    def test_max_delay_sec_not_a_number(self):
        with self.assertRaises(ValidationError) as context:
            TaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                wait_for_receipt=False,
                txn_wait_timeout_sec=-1,

                min_delay_sec=-1,
                max_delay_sec="not a number",

                test_mode=True,
            )

        self.assertTrue("Max Delay should be a float" in str(context.exception))

    def test_max_delay_sec_not_positive(self):
        with self.assertRaises(ValidationError) as context:
            TaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                wait_for_receipt=False,
                txn_wait_timeout_sec=-1,

                min_delay_sec=-1,
                max_delay_sec=-1,

                test_mode=True,
            )

        self.assertTrue("Max Delay should be > 0" in str(context.exception))

    def test_max_delay_sec_greater_than_min_delay_sec(self):
        with self.assertRaises(ValidationError) as context:
            TaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                wait_for_receipt=False,
                txn_wait_timeout_sec=-1,

                min_delay_sec=10,
                max_delay_sec=9,

                test_mode=True,
            )

        self.assertTrue("Max Delay should be > 10" in str(context.exception))

    def test_max_fee_not_a_number(self):
        with self.assertRaises(ValidationError) as context:
            TaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee="not a number",
                forced_gas_limit=False,
            )

        self.assertTrue("Max Fee should be an integer" in str(context.exception))

    def test_max_fee_not_positive(self):
        with self.assertRaises(ValidationError) as context:
            TaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=-1,
                forced_gas_limit=False,
            )

        self.assertTrue("Max Fee should be > 0" in str(context.exception))


class TestAddLiquidityTaskBase(unittest.TestCase):

    def test_amount_out_x_not_a_number(self):
        with self.assertRaises(ValidationError) as context:
            AddLiquidityTaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                coin_x="A",
                coin_y="B",

                use_all_balance_x=False,
                send_percent_balance_x=False,

                min_amount_out_x="not a number",
                max_amount_out_x=1,
            )

        self.assertTrue("Min Amount Out X should be a float" in str(context.exception))
        self.assertTrue("Min Amount Out X is required" in str(context.exception))

        with self.assertRaises(ValidationError) as context:
            AddLiquidityTaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                coin_x="A",
                coin_y="B",

                use_all_balance_x=False,
                send_percent_balance_x=False,

                min_amount_out_x=1,
                max_amount_out_x="not a number",
            )

        self.assertTrue("Max Amount Out X should be a float" in str(context.exception))

    def test_max_amount_lower_than_min_amount(self):
        with self.assertRaises(ValidationError) as context:
            AddLiquidityTaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                coin_x="A",
                coin_y="B",

                use_all_balance_x=False,
                send_percent_balance_x=False,

                min_amount_out_x=10,
                max_amount_out_x=9,
            )

        self.assertTrue("Max Amount Out X should be >= 10" in str(context.exception))

    def test_amount_out_x_not_positive(self):
        with self.assertRaises(ValidationError) as context:
            AddLiquidityTaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                coin_x="A",
                coin_y="B",

                use_all_balance_x=False,
                send_percent_balance_x=False,

                min_amount_out_x=-1,
                max_amount_out_x=1,
            )

        self.assertTrue("Min Amount Out X should be > 0" in str(context.exception))

        with self.assertRaises(ValidationError) as context:
            AddLiquidityTaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                coin_x="A",
                coin_y="B",

                use_all_balance_x=False,
                send_percent_balance_x=False,

                min_amount_out_x=1,
                max_amount_out_x=-1,
            )

        self.assertTrue("Max Amount Out X should be > 0" in str(context.exception))


class TestSwapTaskBase(unittest.TestCase):

    def test_coin_to_receive_equal_to_coin_to_swap(self):
        with self.assertRaises(ValidationError) as context:
            SwapTaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                coin_to_swap="A",
                coin_to_receive="A",

                use_all_balance=False,
                send_percent_balance=False,

                compare_with_cg_price=True,

                min_amount_out=1,
                max_amount_out=1,

                max_price_difference_percent=1,

                slippage=1,
            )

        self.assertTrue("Coin to receive cannot be the same as Coin to swap" in str(context.exception))

    def test_max_price_difference_percent_not_a_number(self):
        with self.assertRaises(ValidationError) as context:
            SwapTaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                coin_to_swap="A",
                coin_to_receive="B",

                use_all_balance=False,
                send_percent_balance=False,

                compare_with_cg_price=True,

                min_amount_out=1,
                max_amount_out=1,

                max_price_difference_percent="not a number",

                slippage=1,
            )

        self.assertTrue("Max Price Difference Percent should be a float" in str(context.exception))

    def test_max_price_difference_percent_not_positive(self):
        with self.assertRaises(ValidationError) as context:
            SwapTaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                coin_to_swap="A",
                coin_to_receive="B",

                use_all_balance=False,
                send_percent_balance=False,

                compare_with_cg_price=True,

                min_amount_out=1,
                max_amount_out=1,

                max_price_difference_percent=-1,

                slippage=1,
            )

        self.assertTrue("Max Price Difference Percent should be >= 0" in str(context.exception))

    def test_max_price_difference_percent_greater_than_100(self):
        with self.assertRaises(ValidationError) as context:
            SwapTaskBase(
                module_type=enums.ModuleType.TEST,
                module_name=enums.ModuleName.TEST,

                max_fee=100,
                forced_gas_limit=False,

                coin_to_swap="A",
                coin_to_receive="B",

                use_all_balance=False,
                send_percent_balance=False,

                compare_with_cg_price=True,

                min_amount_out=1,
                max_amount_out=1,

                max_price_difference_percent=101,

                slippage=1,
            )

        self.assertTrue("Max Price Difference Percent should be < 100" in str(context.exception))
