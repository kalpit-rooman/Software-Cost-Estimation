"""Phase 4 – Chat endpoint."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from schemas.request_response import ChatRequest, ChatResponse, ChatMessage
from services.chatbot import chat as chatbot_chat

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Estimation"],
    summary="Session-aware chatbot — ask questions about your cost estimate",
    responses={
        502: {"description": "Groq API error"},
        503: {"description": "GROQ_API_KEY not configured"},
    },
)
def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """
    Context-aware chatbot powered by Groq (llama-3.3-70b-versatile).

    Accepts the current estimation session data plus conversation history.
    The backend builds a system prompt from the preloaded cost-estimation
    knowledge base and the user's estimation results, then calls Groq.

    Returns the assistant reply and the updated conversation history.
    """
    try:
        reply, updated_history = chatbot_chat(
            message=payload.message,
            context=payload.context,
            history=payload.history,
        )
    except RuntimeError as exc:
        msg = str(exc)
        if "GROQ_API_KEY" in msg:
            raise HTTPException(status_code=503, detail=msg) from exc
        raise HTTPException(status_code=502, detail=msg) from exc

    return ChatResponse(
        reply=reply,
        history=[ChatMessage(role=h.role, content=h.content) for h in updated_history],
    )
