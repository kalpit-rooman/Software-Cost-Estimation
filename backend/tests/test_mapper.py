from __future__ import annotations

import unittest

from services.mapper import UniversalMapper
from schemas.request_response import (
    ComplexityLevel,
    InternalRoute,
    NormalizedUniversalProjectBrief,
    ReliabilityLevel,
)


class UniversalMapperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mapper = UniversalMapper()
        self.brief = NormalizedUniversalProjectBrief(
            num_screens=20,
            num_entities=25,
            duration_months=8.0,
            team_experience_years=5.0,
            pm_experience_years=6.0,
            complexity=ComplexityLevel.medium,
            reliability=ReliabilityLevel.high,
            team_size=8,
            project_notes="workflow platform",
        )

    def test_china_mapping_contains_core_keys(self) -> None:
        mapped, diagnostics = self.mapper.assemble(
            route=InternalRoute.china,
            brief=self.brief,
            follow_up_answers={
                "transaction_volume": 40000,
                "change_request_volume": 180,
                "integration_points": 12,
            },
        )

        for key in ["AFP", "Input", "Output", "Added", "Changed", "Duration"]:
            self.assertIn(key, mapped)

        self.assertEqual(diagnostics.internal_route, InternalRoute.china)
        self.assertGreaterEqual(diagnostics.mapping_confidence, 0.0)
        self.assertLessEqual(diagnostics.mapping_confidence, 1.0)

    def test_cocomo_mapping_contains_core_keys(self) -> None:
        mapped, diagnostics = self.mapper.assemble(
            route=InternalRoute.cocomo81,
            brief=self.brief,
            follow_up_answers={
                "estimated_kloc": 45.0,
                "platform_constraint_level": "tight",
                "tooling_maturity": "medium",
            },
        )

        for key in ["loc", "rely", "cplx", "acap", "aexp", "tool"]:
            self.assertIn(key, mapped)

        self.assertEqual(diagnostics.internal_route, InternalRoute.cocomo81)

    def test_desharnais_mapping_contains_core_keys(self) -> None:
        mapped, diagnostics = self.mapper.assemble(
            route=InternalRoute.desharnais,
            brief=self.brief,
            follow_up_answers={
                "business_process_count": 40,
                "expected_change_requests": 120,
                "data_complexity_index": 6.2,
            },
        )

        for key in ["Length", "TeamExp", "ManagerExp", "Transactions", "Entities", "Adjustment"]:
            self.assertIn(key, mapped)

        self.assertEqual(diagnostics.internal_route, InternalRoute.desharnais)


if __name__ == "__main__":
    unittest.main()
