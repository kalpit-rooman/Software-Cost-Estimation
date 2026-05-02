"""
Tests for cost/currency conversion (services/cost_converter.py,
services/currency_converter.py) – Phase 11.

Run from backend/ directory:
    python -m pytest tests/ -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest

from services.cost_converter import effort_to_inr
from services.currency_converter import SUPPORTED_CURRENCIES, convert_from_inr, get_rate


class TestEffortToInr(unittest.TestCase):
    def test_basic_conversion(self) -> None:
        result = effort_to_inr(10.0, 150_000)
        self.assertAlmostEqual(result, 1_500_000.0)

    def test_fractional_effort(self) -> None:
        result = effort_to_inr(1.5, 100_000)
        self.assertAlmostEqual(result, 150_000.0)

    def test_rounded_to_two_decimal_places(self) -> None:
        result = effort_to_inr(3.0, 99_999)
        self.assertAlmostEqual(result, round(3.0 * 99_999, 2))

    def test_zero_effort_raises(self) -> None:
        with self.assertRaises(ValueError):
            effort_to_inr(0, 150_000)

    def test_negative_effort_raises(self) -> None:
        with self.assertRaises(ValueError):
            effort_to_inr(-5, 150_000)

    def test_zero_rate_raises(self) -> None:
        with self.assertRaises(ValueError):
            effort_to_inr(10, 0)


class TestCurrencyConverter(unittest.TestCase):
    def test_inr_to_inr_is_identity(self) -> None:
        cost, rate = convert_from_inr(1_000_000, "INR")
        self.assertAlmostEqual(cost, 1_000_000)
        self.assertAlmostEqual(rate, 1.0)

    def test_inr_to_usd_produces_smaller_value(self) -> None:
        cost, rate = convert_from_inr(1_000_000, "USD")
        self.assertLess(cost, 1_000_000)
        self.assertGreater(rate, 0)

    def test_unsupported_currency_raises(self) -> None:
        with self.assertRaises(ValueError):
            convert_from_inr(1_000_000, "XYZ")

    def test_all_supported_currencies_convert(self) -> None:
        for currency in SUPPORTED_CURRENCIES:
            cost, rate = convert_from_inr(1_000_000, currency)
            self.assertGreater(cost, 0, f"Conversion to {currency} should be positive")
            self.assertGreater(rate, 0, f"Rate for {currency} should be positive")

    def test_get_rate_inr(self) -> None:
        self.assertAlmostEqual(get_rate("INR"), 1.0)

    def test_get_rate_invalid_raises(self) -> None:
        with self.assertRaises(ValueError):
            get_rate("INVALID")


if __name__ == "__main__":
    unittest.main()
