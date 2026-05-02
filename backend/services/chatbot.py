"""
Chatbot service — Phase 4.

Builds context-aware prompts from estimation session data and the
preloaded cost-estimation knowledge base, then calls Groq via the
existing OpenAI-compatible httpx adapter.
"""
from __future__ import annotations

import httpx

import core.config as cfg
from schemas.request_response import ChatMessage, EstimationContext

# ---------------------------------------------------------------------------
# Groq connection config  (overridable via env / core.config)
# ---------------------------------------------------------------------------
_GROQ_BASE_URL = cfg.OPENAI_BASE_URL or "https://api.groq.com/openai/v1"
_GROQ_MODEL = cfg.AI_MODEL or "llama-3.3-70b-versatile"
_TIMEOUT_S = 30.0
_MAX_TOKENS = 512

# ---------------------------------------------------------------------------
# Preloaded knowledge base embedded in the system prompt
# ---------------------------------------------------------------------------
_KNOWLEDGE = """
## Cost Estimation Knowledge Base

### COCOMO-81 (Constructive Cost Model)
- Developed by Barry Boehm in 1981. Estimates effort from KLOC.
- Cost drivers: RELY, CPLX, ACAP, AEXP, TOOL, SCED.
- Formula: Effort = a × (KLOC^b) × EAF.
- Typical range: 2–500 person-months.

### Desharnais Dataset (Function Point Based)
- 77 business application projects from a Canadian software house.
- Size measured in function points (FP).
- Key predictors: PointsNonAdjust, Adjustment, TeamExp, ManagerExp.
- Typical range: 5–500 person-months.

### China Dataset (Adaptive Function Points)
- 499 projects from a Chinese productivity study.
- Uses Adjusted Function Points (AFP) as primary size measure.
- Typical range: 10–2000 person-months.

### Key Concepts
- **Person-month**: One person working full-time for one month. 12 PM = 1 person for 1 year.
- **Confidence**: How well inputs mapped to model training data. 90% = excellent, 55% = sparse.
- **Cost formula**: Cost = Effort × Monthly blended rate per person.

### Reducing Cost
- Increase team experience
- Reduce scope (fewer screens/entities)
- Improve tooling maturity
- Leverage code reuse
- Phase delivery into shorter iterations
"""

# ---------------------------------------------------------------------------
# System prompt builder
# ---------------------------------------------------------------------------
_DATASET_LABELS = {
    "cocomo81": "COCOMO-81 (large, code-heavy systems)",
    "desharnais": "Desharnais (business apps, function-point based)",
    "china": "China (medium enterprise systems)",
}


def _build_system_prompt(ctx: EstimationContext) -> str:
    dataset_label = _DATASET_LABELS.get(ctx.dataset, ctx.dataset)
    confidence_pct = round(ctx.confidence * 100)

    context_block = f"""
## Current Estimation Session

The user just received an estimate with these results:

- **Dataset**: {dataset_label}
- **Effort**: {ctx.effort_months:.2f} person-months
- **Confidence**: {confidence_pct}%
- **Mode**: {ctx.prediction_mode}
- **Cost**: {ctx.display_cost:,.0f} {ctx.target_currency}
- **Base cost (INR)**: {ctx.base_cost_inr:,.0f} INR
- **Monthly rate**: {ctx.monthly_rate_inr:,.0f} INR/person
- **Exchange rate**: 1 INR = {ctx.exchange_rate:.4f} {ctx.target_currency}
- **Assumptions**: {'; '.join(ctx.assumptions) if ctx.assumptions else 'None'}
- **Warnings**: {'; '.join(ctx.warnings) if ctx.warnings else 'None'}
"""

    return f"""You are SoftEstimate's cost estimation assistant.

ROLE: Help users understand their software project cost estimate. Answer questions about methodology, explain assumptions/warnings, and give actionable advice.

RESPONSE RULES — follow these strictly:
1. Keep answers SHORT. Use 2-3 sentences for simple questions, up to 2 short paragraphs for complex ones.
2. Use bullet points (•) when listing multiple items. Never mix numbered lists into prose text.
3. Use **bold** for key figures, terms, and important values.
4. Separate different topics with a blank line between paragraphs.
5. Never repeat the full estimation results back — the user already sees them. Reference specific values only when explaining something.
6. If you don't know something, say so honestly in one sentence.
7. Politely decline off-topic requests in one sentence.
8. Do NOT use headers (##) in your responses — keep it conversational.

{_KNOWLEDGE}

{context_block}

Answer questions about this estimate and software cost estimation in general. Stay focused on software engineering and cost estimation topics."""


# ---------------------------------------------------------------------------
# Chat function
# ---------------------------------------------------------------------------

def chat(
    message: str,
    context: EstimationContext,
    history: list[ChatMessage],
) -> tuple[str, list[ChatMessage]]:
    """
    Send a message to the Groq chatbot and return the reply plus updated history.

    Args:
        message:   The new user message.
        context:   The serialised estimation result for this session.
        history:   Previous turns in the conversation.

    Returns:
        (reply_text, updated_history)

    Raises:
        RuntimeError: if the Groq API call fails.
    """
    api_key = cfg.GROQ_API_KEY
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add it to backend/.env to enable the chatbot."
        )

    system_prompt = _build_system_prompt(context)

    # Build message list: system + history + new user message
    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    for turn in history:
        messages.append({"role": turn.role, "content": turn.content})
    messages.append({"role": "user", "content": message})

    url = f"{_GROQ_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _GROQ_MODEL,
        "messages": messages,
        "max_tokens": _MAX_TOKENS,
        "temperature": 0.4,
    }

    try:
        with httpx.Client(timeout=_TIMEOUT_S) as client:
            response = client.post(url, headers=headers, json=payload)
    except httpx.TimeoutException as exc:
        raise RuntimeError("Groq API timed out. Try again in a moment.") from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"Network error calling Groq: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"Groq API returned HTTP {response.status_code}: {response.text[:400]}"
        )

    data = response.json()
    try:
        reply = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected Groq response shape: {data}") from exc

    # Update history
    updated_history = list(history) + [
        ChatMessage(role="user", content=message),
        ChatMessage(role="assistant", content=reply),
    ]

    return reply, updated_history
