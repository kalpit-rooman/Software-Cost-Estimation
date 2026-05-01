from __future__ import annotations

# ---------------------------------------------------------------------------
# Cost Converter – Phase 6
# ---------------------------------------------------------------------------
# Derives INR cost from effort (person-months) and a monthly blended rate.
# INR is the canonical internal currency. All other currencies are display
# conversions applied downstream.
# ---------------------------------------------------------------------------


def effort_to_inr(
    effort_months: float,
    monthly_rate_inr: float,
) -> float:
    """
    Convert effort (person-months) to a rupee cost.

    Parameters
    ----------
    effort_months:
        Total estimated effort in person-months.
    monthly_rate_inr:
        Blended monthly rate per person in INR (admin-configurable).

    Returns
    -------
    float
        Base cost in INR, rounded to 2 decimal places.
    """
    if effort_months <= 0:
        raise ValueError(f"effort_months must be positive, got {effort_months}.")
    if monthly_rate_inr <= 0:
        raise ValueError(f"monthly_rate_inr must be positive, got {monthly_rate_inr}.")
    return round(effort_months * monthly_rate_inr, 2)
