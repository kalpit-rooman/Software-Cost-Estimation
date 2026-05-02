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

        raw_prediction = float(ml_result["ensemble_prediction"])
        raw_rf = float(ml_result.get("rf_prediction", raw_prediction))
        raw_xgb = float(ml_result.get("xgb_prediction", raw_prediction))
        raw_lr = float(ml_result.get("lr_prediction", raw_prediction))
        best_model = str(ml_result.get("best_model", "ensemble"))

        # China and Desharnais datasets record effort in person-HOURS.
        # COCOMO-81 records effort directly in person-months.
        # Convert to a common unit (person-months) before any further processing.
        _HOURS_PER_MONTH = 160.0
        _HOUR_BASED_ROUTES = {"china", "desharnais"}
        if route in _HOUR_BASED_ROUTES:
            effort_months = raw_prediction / _HOURS_PER_MONTH
            effort_rf = raw_rf / _HOURS_PER_MONTH
            effort_xgb = raw_xgb / _HOURS_PER_MONTH
            effort_lr = raw_lr / _HOURS_PER_MONTH
        else:
            effort_months = raw_prediction
            effort_rf = raw_rf
            effort_xgb = raw_xgb
            effort_lr = raw_lr

        # Guard: EstimatedEffort schema caps at 600 person-months.
        _EFFORT_CAP = 600.0
        capped = effort_months > _EFFORT_CAP
        if capped:
            effort_months = _EFFORT_CAP

        # Compute cost range from the spread of individual model predictions.
        individual_efforts = [effort_rf, effort_xgb, effort_lr]
        optimistic_effort = max(0.1, min(individual_efforts))
        pessimistic_effort = max(individual_efforts) * 1.15  # 15% risk buffer
        most_likely_effort = effort_months

        assumptions = [
            "Effort derived from an ensemble of calibrated ML models (CNN, MLP, baselines).",
            f"Internal estimation route: {route}.",
        ]
        warnings: list[str] = []
        if capped:
            warnings.append(
                "Predicted effort exceeded the estimation ceiling (600 person-months). "
                "Result has been capped. Consider breaking the project into phases."
            )
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
            "model_predictions": {
                "random_forest": round(effort_rf, 2),
                "xgboost": round(effort_xgb, 2),
                "linear_regression": round(effort_lr, 2),
                "ensemble": round(effort_months, 2),
                "best_model": best_model,
            },
            "cost_range": {
                "optimistic_effort": round(optimistic_effort, 2),
                "most_likely_effort": round(most_likely_effort, 2),
                "pessimistic_effort": round(pessimistic_effort, 2),
            },
        }

