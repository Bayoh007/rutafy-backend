"""Supabase JWT verification primitives."""

from typing import Any

import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient

from app.core.config import get_settings


class TokenVerifier:
    """Verifies Supabase JWTs against the project's JWKS endpoint."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._jwks_client = (
            PyJWKClient(str(self.settings.supabase_jwks_url))
            if self.settings.supabase_jwks_url
            else None
        )

    def verify(self, token: str) -> dict[str, Any]:
        if not self.settings.supabase_jwt_issuer or not self._jwks_client:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication is not configured.")
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            return jwt.decode(token, signing_key.key, algorithms=["ES256", "RS256"], audience=self.settings.supabase_jwt_audience, issuer=self.settings.supabase_jwt_issuer, options={"require": ["exp", "sub"]})
        except jwt.PyJWTError as error:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token.", headers={"WWW-Authenticate": "Bearer"}) from error
