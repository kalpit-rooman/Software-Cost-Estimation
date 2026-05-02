from schemas.request_response import RiskFactor

def assess_risks(complexity: str, reliability: str, base_effort: float, monthly_rate_inr: float) -> list[RiskFactor]:
    """
    Generate a list of project risks based on user inputs.
    """
    risks = []
    
    # Complexity Risks
    if complexity.lower() == "high":
        risks.append(
            RiskFactor(
                risk_name="Complex Architecture Integration",
                impact_level="High",
                probability="Medium",
                mitigation="Allocate senior architects to the design phase. Implement strict CI/CD and automated integration tests.",
                potential_cost_impact_inr=base_effort * 0.15 * monthly_rate_inr
            )
        )
    elif complexity.lower() == "medium":
        risks.append(
            RiskFactor(
                risk_name="Scope Creep due to Feature Ambiguity",
                impact_level="Medium",
                probability="Medium",
                mitigation="Implement strict agile sprint planning and freeze requirements before each sprint.",
                potential_cost_impact_inr=base_effort * 0.10 * monthly_rate_inr
            )
        )

    # Reliability Risks
    if reliability.lower() == "high":
        risks.append(
            RiskFactor(
                risk_name="Stringent Compliance & QA Overhead",
                impact_level="High",
                probability="High",
                mitigation="Shift-left testing. Invest heavily in automated end-to-end testing frameworks early in the SDLC.",
                potential_cost_impact_inr=base_effort * 0.20 * monthly_rate_inr
            )
        )
        
    # General Delivery Risk
    risks.append(
        RiskFactor(
            risk_name="Resource Attrition / Unavailability",
            impact_level="High",
            probability="Low",
            mitigation="Ensure extensive documentation and cross-training among team members to prevent single points of failure.",
            potential_cost_impact_inr=base_effort * 0.12 * monthly_rate_inr
        )
    )

    return risks
