from __future__ import annotations

from schemas.request_response import (
    ComplexityLevel,
    InternalRoute,
    MappingDiagnostics,
    NormalizedUniversalProjectBrief,
    ReliabilityLevel,
)


class UniversalMapper:
    def assemble(
        self,
        route: InternalRoute,
        brief: NormalizedUniversalProjectBrief,
        follow_up_answers: dict[str, object],
        unresolved_fields: list[str] | None = None,
    ) -> tuple[dict[str, float], MappingDiagnostics]:
        unresolved = unresolved_fields or []

        if route == InternalRoute.china:
            mapped = self._map_china(brief, follow_up_answers)
            rationale = [
                "Mapped volume and change-related indicators into AFP-style workload signals.",
                "Mapped duration and team profile into delivery capacity proxies.",
            ]
        elif route == InternalRoute.cocomo81:
            mapped = self._map_cocomo81(brief, follow_up_answers)
            rationale = [
                "Mapped complexity and reliability into cost-driver equivalents.",
                "Mapped team and schedule constraints into capability/tooling factors.",
            ]
        else:
            mapped = self._map_desharnais(brief, follow_up_answers)
            rationale = [
                "Mapped process and data scope into transactions/entities proxies.",
                "Mapped management and team experience into effort adjustment factors.",
            ]

        confidence = self._mapping_confidence(unresolved)
        diagnostics = MappingDiagnostics(
            internal_route=route,
            mapping_confidence=confidence,
            mapping_rationale=rationale,
            unresolved_fields=unresolved,
        )
        return mapped, diagnostics

    @staticmethod
    def _mapping_confidence(unresolved_fields: list[str]) -> float:
        if not unresolved_fields:
            return 0.9
        penalty = min(len(unresolved_fields) * 0.08, 0.24)
        return round(0.9 - penalty, 4)

    @staticmethod
    def _complexity_rank(complexity: ComplexityLevel) -> int:
        return {
            ComplexityLevel.low: 1,
            ComplexityLevel.medium: 2,
            ComplexityLevel.high: 3,
        }[complexity]

    @staticmethod
    def _reliability_rank(reliability: ReliabilityLevel) -> int:
        return {
            ReliabilityLevel.low: 1,
            ReliabilityLevel.medium: 2,
            ReliabilityLevel.high: 3,
        }[reliability]

    def _map_china(self, brief: NormalizedUniversalProjectBrief, answers: dict[str, object]) -> dict[str, float]:
        complexity_rank = self._complexity_rank(brief.complexity)
        reliability_rank = self._reliability_rank(brief.reliability)

        tx_volume = float(answers.get("transaction_volume", max(10, brief.num_screens * 120)))
        change_volume = float(answers.get("change_request_volume", brief.num_entities * 4))
        integration_points = float(answers.get("integration_points", brief.team_size))
        reuse_percent = float(answers.get("expected_reuse_percent", 20.0))

        afp = max(20.0, (brief.num_screens * 9.0) + (brief.num_entities * 6.0) + (tx_volume / 250.0))
        added = max(5.0, (change_volume * 0.45) + (brief.num_entities * 1.5))
        changed = max(2.0, (change_volume * 0.35) + (brief.num_screens * 0.9))
        deleted = max(0.0, change_volume * 0.2)
        duration = max(1.0, brief.duration_months)

        return {
            "AFP": round(afp, 4),
            "Input": round(max(5.0, tx_volume * 0.22), 4),
            "Output": round(max(5.0, tx_volume * 0.28 + integration_points * 0.5), 4),
            "Enquiry": round(max(1.0, tx_volume * 0.08), 4),
            "File": round(max(1.0, brief.num_entities * 0.8), 4),
            "Interface": round(max(0.0, integration_points), 4),
            "Added": round(added, 4),
            "Changed": round(changed, 4),
            "Deleted": round(deleted, 4),
            "Resource": round(max(1.0, brief.team_size), 4),
            "Dev.Type": 0.0,
            "Duration": round(duration, 4),
            "ComplexityIndex": float(complexity_rank),
            "ReliabilityIndex": float(reliability_rank),
            "ReusePercent": round(reuse_percent, 4),
        }

    def _map_cocomo81(self, brief: NormalizedUniversalProjectBrief, answers: dict[str, object]) -> dict[str, float]:
        complexity_rank = self._complexity_rank(brief.complexity)
        reliability_rank = self._reliability_rank(brief.reliability)

        estimated_kloc = float(answers.get("estimated_kloc", max(1.0, brief.num_screens * 0.8 + brief.num_entities * 0.35)))
        platform_constraint_level = str(answers.get("platform_constraint_level", "nominal"))
        tooling_maturity = str(answers.get("tooling_maturity", "medium"))
        schedule_compression = str(answers.get("schedule_compression", "medium"))

        platform_scale = {"relaxed": 0.9, "nominal": 1.0, "tight": 1.18}
        tooling_scale = {"low": 1.15, "medium": 1.0, "high": 0.88}
        compression_scale = {"low": 0.92, "medium": 1.0, "high": 1.14}
        reliability_scale = {1: 0.88, 2: 1.0, 3: 1.15}
        complexity_scale = {1: 0.85, 2: 1.0, 3: 1.18}

        acap = max(0.7, 1.22 - (brief.team_experience_years * 0.05))
        aexp = max(0.72, 1.18 - (brief.pm_experience_years * 0.04))

        return {
            "loc": round(max(1.0, estimated_kloc), 4),
            "rely": round(reliability_scale[reliability_rank], 4),
            "cplx": round(complexity_scale[complexity_rank] * platform_scale.get(platform_constraint_level, 1.0), 4),
            "acap": round(acap, 4),
            "aexp": round(aexp, 4),
            "tool": round(tooling_scale.get(tooling_maturity, 1.0), 4),
            "sced": round(compression_scale.get(schedule_compression, 1.0), 4),
            "team_size_signal": round(float(brief.team_size), 4),
            "duration_signal": round(float(brief.duration_months), 4),
        }

    def _map_desharnais(self, brief: NormalizedUniversalProjectBrief, answers: dict[str, object]) -> dict[str, float]:
        complexity_rank = self._complexity_rank(brief.complexity)
        reliability_rank = self._reliability_rank(brief.reliability)

        process_count = float(answers.get("business_process_count", max(1, brief.num_screens * 2)))
        change_requests = float(answers.get("expected_change_requests", max(0, brief.num_entities * 3)))
        data_complexity = float(answers.get("data_complexity_index", 5.0))
        team_distribution = str(answers.get("team_distribution", "hybrid"))

        distribution_scale = {
            "co_located": 0.95,
            "hybrid": 1.0,
            "distributed": 1.1,
        }

        transactions = max(10.0, process_count * 2.1 + change_requests * 0.8)
        entities = max(5.0, brief.num_entities * 1.2 + data_complexity * 1.5)
        points_non_adjust = max(20.0, brief.num_screens * 10.0 + entities * 0.6)
        adjustment = max(10.0, min(60.0, 18.0 + complexity_rank * 8.0 + reliability_rank * 5.0 + data_complexity * 1.2))

        return {
            "Length": round(float(brief.duration_months), 4),
            "TeamExp": round(float(brief.team_experience_years), 4),
            "ManagerExp": round(float(brief.pm_experience_years), 4),
            "Transactions": round(transactions * distribution_scale.get(team_distribution, 1.0), 4),
            "Entities": round(entities, 4),
            "PointsNonAdjust": round(points_non_adjust, 4),
            "Adjustment": round(adjustment, 4),
            "Language": 1.0 if complexity_rank == 1 else 2.0 if complexity_rank == 2 else 3.0,
            "ChangeRequests": round(change_requests, 4),
        }
