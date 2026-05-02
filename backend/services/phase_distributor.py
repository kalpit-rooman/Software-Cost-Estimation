from schemas.request_response import PhaseBreakdown

BASE_DISTRIBUTION = {
    "Requirements & Design": 0.15,
    "Development": 0.45,
    "Testing & QA": 0.25,
    "Deployment & DevOps": 0.10,
    "Project Management": 0.05,
}

def distribute_phases(
    effort_months: float,
    monthly_rate_inr: float,
    complexity: str,
    reliability: str
) -> list[PhaseBreakdown]:
    """
    Distribute total effort into SDLC phases based on project characteristics.
    """
    distribution = BASE_DISTRIBUTION.copy()

    # Adjust based on complexity
    if complexity.lower() == "high":
        distribution["Requirements & Design"] += 0.05
        distribution["Development"] -= 0.05

    # Adjust based on reliability
    if reliability.lower() == "high":
        distribution["Testing & QA"] += 0.05
        distribution["Development"] -= 0.05

    breakdown = []
    for phase_name, percentage in distribution.items():
        phase_effort = effort_months * percentage
        phase_cost = phase_effort * monthly_rate_inr
        breakdown.append(
            PhaseBreakdown(
                phase_name=phase_name,
                percentage=round(percentage * 100, 2),
                effort_months=round(phase_effort, 2),
                cost_inr=round(phase_cost, 2)
            )
        )
    return breakdown
