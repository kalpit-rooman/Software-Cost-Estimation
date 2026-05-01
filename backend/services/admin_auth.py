"""
Admin authentication dependency (Phase 9).

Verifies a bearer token against the ADMIN_API_KEY environment variable.
Mount this as a FastAPI dependency on any protected admin endpoint.
"""
from __future__ import annotations

import os

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=False)


def require_admin_key(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> None:
    """
    FastAPI dependency that enforces admin bearer-token auth.

    Raises:
        503  – ADMIN_API_KEY is not configured on the server.
        401  – Token is missing or does not match ADMIN_API_KEY.
    """
    admin_key = os.getenv("ADMIN_API_KEY", "")
    if not admin_key:
        raise HTTPException(
            status_code=503,
            detail="Admin access is not configured. Set ADMIN_API_KEY on the server.",
        )
    if credentials is None or credentials.credentials != admin_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing admin token. Provide the correct key as a Bearer token.",
        )
