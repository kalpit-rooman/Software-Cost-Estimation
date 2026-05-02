"""
Tests for guardrails (services/guardrails.py) – Phase 11.

Run from backend/ directory:
    python -m pytest tests/ -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest

from services.guardrails import GuardrailViolation, validate_effort_response


def _valid_response(**overrides) -> dict:
    base = {
        "effort_months": 12.0,
        "confidence": 0.75,
        "assumptions": ["Team works 22 days/month."],
        "warnings": [],
    }
    base.update(overrides)
    return base


class TestGuardrails(unittest.TestCase):
    def test_valid_response_passes(self) -> None:
        result = validate_effort_response(_valid_response())
        self.assertEqual(result["effort_months"], 12.0)

    def test_effort_below_minimum_fails(self) -> None:
        with self.assertRaises(GuardrailViolation):
            validate_effort_response(_valid_response(effort_months=0.1))

    def test_effort_above_maximum_fails(self) -> None:
        with self.assertRaises(GuardrailViolation):
            validate_effort_response(_valid_response(effort_months=700.0))

    def test_negative_confidence_fails(self) -> None:
        with self.assertRaises(GuardrailViolation):
            validate_effort_response(_valid_response(confidence=-0.1))

    def test_confidence_above_one_fails(self) -> None:
        with self.assertRaises(GuardrailViolation):
            validate_effort_response(_valid_response(confidence=1.5))

    def test_oversized_assumptions_list_clamped(self) -> None:
        long_list = [f"assumption {i}" for i in range(30)]
        result = validate_effort_response(_valid_response(assumptions=long_list))
        self.assertLessEqual(len(result["assumptions"]), 20)

    def test_oversized_warnings_list_clamped(self) -> None:
        long_list = [f"warning {i}" for i in range(30)]
        result = validate_effort_response(_valid_response(warnings=long_list))
        self.assertLessEqual(len(result["warnings"]), 20)

    def test_boundary_minimum_effort_passes(self) -> None:
        result = validate_effort_response(_valid_response(effort_months=0.5))
        self.assertEqual(result["effort_months"], 0.5)

    def test_boundary_maximum_effort_passes(self) -> None:
        result = validate_effort_response(_valid_response(effort_months=600.0))
        self.assertEqual(result["effort_months"], 600.0)

    def test_zero_confidence_passes(self) -> None:
        result = validate_effort_response(_valid_response(confidence=0.0))
        self.assertEqual(result["confidence"], 0.0)

    def test_full_confidence_passes(self) -> None:
        result = validate_effort_response(_valid_response(confidence=1.0))
        self.assertEqual(result["confidence"], 1.0)


if __name__ == "__main__":
    unittest.main()
