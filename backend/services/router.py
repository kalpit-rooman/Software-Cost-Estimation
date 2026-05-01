from __future__ import annotations

from typing import TypeAlias

from schemas.request_response import (
    ComplexityLevel,
    InternalRoute,
    NormalizedUniversalProjectBrief,
    ReliabilityLevel,
    RouteInferenceMetadata,
    UniversalProjectBrief,
)

UniversalBrief: TypeAlias = UniversalProjectBrief | NormalizedUniversalProjectBrief


class UniversalRouter:
    FOLLOW_UP_PACK_BY_ROUTE: dict[InternalRoute, str] = {
        InternalRoute.china: "adaptive_pack_alpha",
        InternalRoute.cocomo81: "adaptive_pack_beta",
        InternalRoute.desharnais: "adaptive_pack_gamma",
    }

    def infer_route(self, intake_id: str, brief: UniversalBrief) -> RouteInferenceMetadata:
        scores, contributions = self._score_routes(brief)
        ranked_routes = sorted(scores.items(), key=lambda item: (-item[1], item[0].value))

        selected_route, selected_score = ranked_routes[0]
        second_score = ranked_routes[1][1] if len(ranked_routes) > 1 else 0.0
        confidence = self._calculate_confidence(selected_score, second_score)

        top_signals = sorted(contributions[selected_route], key=lambda item: item[1], reverse=True)
        rationale = [
            f"{reason} ({value:.2f})"
            for reason, value in top_signals
            if value > 0.0
        ][:4]

        route_scores = {route.value: round(score, 4) for route, score in scores.items()}

        return RouteInferenceMetadata(
            intake_id=intake_id,
            detected_route=selected_route,
            follow_up_pack_id=self.FOLLOW_UP_PACK_BY_ROUTE[selected_route],
            routing_confidence=confidence,
            routing_rationale=rationale,
            route_scores=route_scores,
        )

    def _score_routes(self, brief: UniversalBrief) -> tuple[dict[InternalRoute, float], dict[InternalRoute, list[tuple[str, float]]]]:
        scores: dict[InternalRoute, float] = {route: 0.4 for route in InternalRoute}
        contributions: dict[InternalRoute, list[tuple[str, float]]] = {route: [] for route in InternalRoute}

        size_signal = (brief.num_screens * 0.6) + (brief.num_entities * 0.4)
        experience_signal = (brief.team_experience_years + brief.pm_experience_years) / 2.0
        delivery_pressure = size_signal / max(brief.duration_months, 1.0)

        self._add(
            scores,
            contributions,
            InternalRoute.china,
            "screen and entity volume signal",
            self._clamp(size_signal / 45.0, 0.0, 2.5),
        )
        self._add(
            scores,
            contributions,
            InternalRoute.china,
            "delivery pressure signal",
            self._clamp(delivery_pressure / 4.0, 0.0, 1.8),
        )
        self._add(
            scores,
            contributions,
            InternalRoute.china,
            "duration fit signal",
            0.7 if brief.duration_months <= 9.0 else 0.2,
        )

        if brief.complexity == ComplexityLevel.high:
            self._add(scores, contributions, InternalRoute.china, "high complexity multiplier", 1.0)
        elif brief.complexity == ComplexityLevel.medium:
            self._add(scores, contributions, InternalRoute.china, "medium complexity multiplier", 0.6)

        if brief.num_screens > 60 or brief.num_entities > 70:
            self._add(scores, contributions, InternalRoute.china, "large product footprint bonus", 0.9)

        reliability_weight = {
            ReliabilityLevel.low: 0.3,
            ReliabilityLevel.medium: 1.0,
            ReliabilityLevel.high: 2.2,
        }[brief.reliability]
        complexity_weight = {
            ComplexityLevel.low: 0.2,
            ComplexityLevel.medium: 0.9,
            ComplexityLevel.high: 1.7,
        }[brief.complexity]

        self._add(scores, contributions, InternalRoute.cocomo81, "reliability requirement signal", reliability_weight)
        self._add(scores, contributions, InternalRoute.cocomo81, "complexity driver signal", complexity_weight)
        self._add(
            scores,
            contributions,
            InternalRoute.cocomo81,
            "team scale signal",
            self._clamp(brief.team_size / 6.0, 0.0, 2.5),
        )
        self._add(
            scores,
            contributions,
            InternalRoute.cocomo81,
            "schedule horizon signal",
            self._clamp(brief.duration_months / 12.0, 0.0, 2.0),
        )
        self._add(
            scores,
            contributions,
            InternalRoute.cocomo81,
            "experience fit signal",
            self._clamp(experience_signal / 8.0, 0.0, 1.8),
        )

        if brief.team_size >= 10:
            self._add(scores, contributions, InternalRoute.cocomo81, "large team bonus", 0.8)

        if brief.reliability == ReliabilityLevel.high and brief.complexity == ComplexityLevel.high:
            self._add(scores, contributions, InternalRoute.cocomo81, "high risk-control coupling bonus", 0.8)

        self._add(
            scores,
            contributions,
            InternalRoute.desharnais,
            "entity structure signal",
            self._clamp(brief.num_entities / 20.0, 0.0, 2.3),
        )
        self._add(
            scores,
            contributions,
            InternalRoute.desharnais,
            "screen process signal",
            self._clamp(brief.num_screens / 25.0, 0.0, 1.8),
        )
        self._add(
            scores,
            contributions,
            InternalRoute.desharnais,
            "project length fit signal",
            self._clamp(brief.duration_months / 10.0, 0.0, 1.8),
        )
        self._add(
            scores,
            contributions,
            InternalRoute.desharnais,
            "pm experience signal",
            self._clamp(brief.pm_experience_years / 6.0, 0.0, 1.8),
        )
        self._add(
            scores,
            contributions,
            InternalRoute.desharnais,
            "team experience signal",
            self._clamp(brief.team_experience_years / 6.0, 0.0, 1.5),
        )

        if 3 <= brief.team_size <= 12:
            self._add(scores, contributions, InternalRoute.desharnais, "mid-size delivery team bonus", 1.0)

        if brief.complexity in {ComplexityLevel.medium, ComplexityLevel.high}:
            self._add(scores, contributions, InternalRoute.desharnais, "non-trivial complexity bonus", 0.6)

        if brief.project_notes:
            self._add(scores, contributions, InternalRoute.desharnais, "additional requirement context bonus", 0.2)

        return scores, contributions

    @staticmethod
    def _add(
        scores: dict[InternalRoute, float],
        contributions: dict[InternalRoute, list[tuple[str, float]]],
        route: InternalRoute,
        reason: str,
        value: float,
    ) -> None:
        scores[route] += value
        contributions[route].append((reason, value))

    @staticmethod
    def _clamp(value: float, lower: float, upper: float) -> float:
        return max(lower, min(value, upper))

    def _calculate_confidence(self, best_score: float, second_score: float) -> float:
        if best_score <= 0.0:
            return 0.55
        dominance = (best_score - second_score) / best_score
        confidence = self._clamp(0.55 + (dominance * 0.4), 0.55, 0.95)
        return round(confidence, 4)
