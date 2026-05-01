"""
Model-mode orchestrator (Phase 10).

Wraps src/predictor.py behind the same interface as AIOrchestrator so
predict.py can call either path identically.

Return shape:
  {
    "effort_months": float,
    "confidence":    float,   # 0–1, derived from mapping confidence
    "assumptions":   list[str],
    "warnings":      list[str],
  }
"""
from __future__ import annotations

from src.predictor import predict_cost


class ModelOrchestrator:
    """
    Thin adapter around the ensemble ML predictor.

    The public contract mirrors AIOrchestrator.estimate_effort so that
    predict.py can switch between the two with no structural changes.
    """

    def estimate_effort(
        self,
        *,
        route: str,
        mapped_features: dict,
        mapping_confidence: float,
        unresolved_fields: list[str],
        ensemble_method: str = "simple",
        weights: list[float] | None = None,
    ) -> dict:
        """
        Run the ensemble predictor and return a normalised result dict.

        Args:
            route:              Internal route identifier ("china", "cocomo81", "desharnais").
            mapped_features:    Feature dict produced by UniversalMapper.assemble().
            mapping_confidence: 0-1 score from UniversalMapper mapping_diagnostics.
            unresolved_fields:  Fields that fell back to defaults; surfaced in warnings.
            ensemble_method:    Passed straight to predict_cost() ("simple" by default).
            weights:            Optional explicit weights for weighted ensemble.

        Returns:
            dict with keys: effort_months, confidence, assumptions, warnings.

        Raises:
            RuntimeError: wraps any exception from predict_cost() with context.
        """
        try:
            ml_result = predict_cost(
                route,
                mapped_features,
                ensemble_method=ensemble_method,
                weights=weights,
            )
        except Exception as exc:
            raise RuntimeError(
                f"ML prediction failed for route '{route}': {exc}"
            ) from exc

        effort_months = float(ml_result["ensemble_prediction"])

        assumptions = [
            "Effort derived from an ensemble of calibrated ML models (CNN, MLP, baselines).",
            f"Internal estimation route: {route}.",
        ]
        warnings: list[str] = []
        if unresolved_fields:
            warnings.append(
                f"Some inputs used default values: {', '.join(unresolved_fields)}. "
                "Provide more specific values for a sharper estimate."
            )

        return {
            "effort_months": effort_months,
            "confidence": mapping_confidence,
            "assumptions": assumptions,
            "warnings": warnings,
        }
