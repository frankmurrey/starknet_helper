import unittest

from pydantic import BaseModel
from pydantic import ValidationError

from src.schemas.validation_mixins import SlippageValidationMixin
from src.schemas.validation_mixins import SameCoinValidationMixin
from src.schemas.validation_mixins import MinMaxAmountOutValidationMixin


class TestSlippageValidationMixin(unittest.TestCase):
    def test_slippage_not_a_number(self):
        with self.assertRaises(ValidationError) as context:
            SlippageValidationMixin(
                slippage="not a number"
            )

        self.assertTrue("Slippage should be a float" in str(context.exception))

    def test_slippage_not_positive(self):
        with self.assertRaises(ValidationError) as context:
            SlippageValidationMixin(
                slippage=-1
            )

        self.assertTrue("Slippage should be > 0" in str(context.exception))

    def test_slippage_greater_than_100(self):
        with self.assertRaises(ValidationError) as context:
            SlippageValidationMixin(
                slippage=101
            )

        self.assertTrue("Slippage should be < 100" in str(context.exception))


class TestSameCoinValidationMixin(unittest.TestCase):

    def test_coin_y_equal_coin_x(self):
        with self.assertRaises(ValidationError) as context:
            SameCoinValidationMixin(
                coin_x="A",
                coin_y="A"
            )

        self.assertTrue("Coin Y cannot be the same as Coin X" in str(context.exception))


class TestMinMaxAmountOutValidationMixin(unittest.TestCase):

    def test_min_amount_out_not_a_number(self):
        with self.assertRaises(ValidationError) as context:
            MinMaxAmountOutValidationMixin(
                use_all_balance=False,

                min_amount_out="not a number",
                max_amount_out=1,
            )

        self.assertTrue("Min Amount Out should be a float" in str(context.exception))

    def test_min_amount_out_not_positive(self):
        with self.assertRaises(ValidationError) as context:
            MinMaxAmountOutValidationMixin(
                use_all_balance=False,

                min_amount_out=-1,
                max_amount_out=1,
            )

        self.assertTrue("Min Amount Out should be > 0" in str(context.exception))

    def test_max_amount_out_not_a_number(self):
        with self.assertRaises(ValidationError) as context:
            MinMaxAmountOutValidationMixin(
                use_all_balance=False,

                min_amount_out=1,
                max_amount_out="not a number",
            )

        self.assertTrue("Max Amount Out should be a float" in str(context.exception))

    def test_max_amount_out_not_positive(self):
        with self.assertRaises(ValidationError) as context:
            MinMaxAmountOutValidationMixin(
                use_all_balance=False,

                min_amount_out=1,
                max_amount_out=-1,
            )

        self.assertTrue("Max Amount Out should be > 0" in str(context.exception))

    def test_max_amount_out_lower_than_min_amount(self):
        with self.assertRaises(ValidationError) as context:
            MinMaxAmountOutValidationMixin(
                use_all_balance=False,

                min_amount_out=10,
                max_amount_out=9,
            )

        self.assertTrue("Max Amount Out should be >= 10" in str(context.exception))

    def test_min_amount_out_not_set(self):
        with self.assertRaises(ValidationError) as context:
            MinMaxAmountOutValidationMixin(
                use_all_balance=False,

                max_amount_out=1,
            )

        self.assertTrue("Min Amount Out is required" in str(context.exception))