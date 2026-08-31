"""Authentication integration boundary.

Registration, login, email verification, and password recovery are performed by
Supabase Auth. This API only accepts the resulting bearer token.
"""

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.common import CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/session", response_model=CurrentUser)
async def session(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Return the authenticated Supabase identity known to this API."""
    return current_user
