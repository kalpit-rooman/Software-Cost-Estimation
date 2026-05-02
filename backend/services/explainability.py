from schemas.request_response import ExplainabilityStep, TechStack

def generate_waterfall(
    base_ml_effort: float,
    tech_stack: TechStack,
    multiplier: float
) -> list[ExplainabilityStep]:
    """
    Generate explainability waterfall steps showing how the final effort was derived.
    """
    steps = []
    
    # Base ML Prediction
    steps.append(
        ExplainabilityStep(
            step_name="Base ML Prediction",
            effort_change_months=round(base_ml_effort, 2),
            is_base=True,
            description="Initial effort predicted by the ensemble machine learning model based on core project size (screens, entities, etc.)."
        )
    )
    
    # Tech Stack Adjustment
    if multiplier != 1.0:
        adj_effort = (base_ml_effort * multiplier) - base_ml_effort
        steps.append(
            ExplainabilityStep(
                step_name=f"{tech_stack.value.replace('_', ' ').title()} Stack Adjustment",
                effort_change_months=round(adj_effort, 2),
                is_base=False,
                description=f"Applied a {multiplier}x multiplier due to the selected technology stack complexity."
            )
        )

    return steps
