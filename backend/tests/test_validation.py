"""
Tests for validation (schemas/request_response.py) – Phase 11.

Run from backend/ directory:
    python -m pytest tests/ -v
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure backend/ is on the path when running directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest

from pydantic import ValidationError

from schemas.request_response import (
    ComplexityLevel,
    FinalPredictionRequest,
    ReliabilityLevel,
    UniversalPredictionRequest,
    UniversalProjectBrief,
)


def _valid_brief() -> dict:
    return {
        "num_screens": 20,
        "num_entities": 25,
        "duration_months": 8.0,
        "team_experience_years": 5.0,
        "pm_experience_years": 4.0,
        "complexity": "medium",
        "reliability": "high",
        "team_size": 8,
    }


class TestUniversalProjectBriefValidation(unittest.TestCase):
    def test_valid_brief_parses(self) -> None:
        brief = UniversalProjectBrief(**_valid_brief())
        self.assertEqual(brief.num_screens, 20)
        self.assertEqual(brief.complexity, ComplexityLevel.medium)
        self.assertEqual(brief.reliability, ReliabilityLevel.high)

    def test_invalid_complexity_rejected(self) -> None:
        data = {**_valid_brief(), "complexity": "extreme"}
        with self.assertRaises(ValidationError):
            UniversalProjectBrief(**data)

    def test_invalid_reliability_rejected(self) -> None:
        data = {**_valid_brief(), "reliability": "ultra"}
        with self.assertRaises(ValidationError):
            UniversalProjectBrief(**data)

    def test_negative_team_size_rejected(self) -> None:
        data = {**_valid_brief(), "team_size": -1}
        with self.assertRaises(ValidationError):
            UniversalProjectBrief(**data)

    def test_zero_duration_rejected(self) -> None:
        data = {**_valid_brief(), "duration_months": 0}
        with self.assertRaises(ValidationError):
            UniversalProjectBrief(**data)


class TestUniversalPredictionRequestValidation(unittest.TestCase):
    def test_valid_request_parses(self) -> None:
        req = UniversalPredictionRequest(
            project_brief=UniversalProjectBrief(**_valid_brief()),
        )
        self.assertIsNotNone(req.project_brief)

    def test_extra_fields_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            UniversalPredictionRequest(
                project_brief=UniversalProjectBrief(**_valid_brief()),
                unknown_field="bad",
            )


class TestFinalPredictionRequestValidation(unittest.TestCase):
    def test_valid_final_request(self) -> None:
        req = FinalPredictionRequest(
            intake_id="test-uuid",
            follow_up_answers={"transaction_volume": 40000},
        )
        self.assertEqual(req.intake_id, "test-uuid")

    def test_missing_intake_id_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            FinalPredictionRequest(follow_up_answers={})  # type: ignore[call-arg]


if __name__ == "__main__":
    unittest.main()
