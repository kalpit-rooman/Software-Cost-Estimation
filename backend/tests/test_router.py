"""
Tests for UniversalRouter (services/router.py) – Phase 11.

Run from backend/ directory:
    python -m pytest tests/ -v
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest

from schemas.request_response import (
    ComplexityLevel,
    InternalRoute,
    NormalizedUniversalProjectBrief,
    ReliabilityLevel,
)
from services.router import UniversalRouter


def _make_brief(**overrides) -> NormalizedUniversalProjectBrief:
    defaults = dict(
        num_screens=20,
        num_entities=25,
        duration_months=8.0,
        team_experience_years=5.0,
        pm_experience_years=4.0,
        complexity=ComplexityLevel.medium,
        reliability=ReliabilityLevel.high,
        team_size=8,
        project_notes=None,
    )
    defaults.update(overrides)
    return NormalizedUniversalProjectBrief(**defaults)


class TestUniversalRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.router = UniversalRouter()

    def test_returns_route_inference_metadata(self) -> None:
        brief = _make_brief()
        meta = self.router.infer_route(intake_id="test-1", brief=brief)
        self.assertIn(meta.detected_route, list(InternalRoute))

    def test_detected_route_is_one_of_three(self) -> None:
        brief = _make_brief()
        meta = self.router.infer_route(intake_id="test-2", brief=brief)
        self.assertIn(meta.detected_route, {InternalRoute.china, InternalRoute.cocomo81, InternalRoute.desharnais})

    def test_confidence_in_valid_range(self) -> None:
        brief = _make_brief()
        meta = self.router.infer_route(intake_id="test-3", brief=brief)
        self.assertGreaterEqual(meta.routing_confidence, 0.0)
        self.assertLessEqual(meta.routing_confidence, 1.0)

    def test_follow_up_pack_id_not_empty(self) -> None:
        brief = _make_brief()
        meta = self.router.infer_route(intake_id="test-4", brief=brief)
        self.assertTrue(meta.follow_up_pack_id)

    def test_route_scores_covers_all_routes(self) -> None:
        brief = _make_brief()
        meta = self.router.infer_route(intake_id="test-5", brief=brief)
        self.assertEqual(set(meta.route_scores.keys()), {"china", "cocomo81", "desharnais"})

    def test_large_transaction_system_routes_to_china(self) -> None:
        """High num_screens + low kloc hints → china route expected."""
        # Keep cocomo/desharnais signals intentionally weak so china dominates.
        brief = _make_brief(
            num_screens=220,
            num_entities=170,
            duration_months=6.0,
            reliability=ReliabilityLevel.low,
            complexity=ComplexityLevel.low,
            team_size=2,
            team_experience_years=0.0,
            pm_experience_years=0.0,
            project_notes=None,
        )
        meta = self.router.infer_route(intake_id="test-6", brief=brief)
        self.assertEqual(meta.detected_route, InternalRoute.china)

    def test_intake_id_preserved(self) -> None:
        brief = _make_brief()
        meta = self.router.infer_route(intake_id="my-unique-id", brief=brief)
        self.assertEqual(meta.intake_id, "my-unique-id")


if __name__ == "__main__":
    unittest.main()
