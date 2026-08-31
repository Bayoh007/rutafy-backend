import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import TokenVerifier
from app.models import Role, UserRole
from app.schemas.common import CurrentUser

bearer_scheme = HTTPBearer(auto_error=False)
verifier = TokenVerifier()


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> CurrentUser:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    claims = verifier.verify(credentials.credentials)
    return CurrentUser(id=uuid.UUID(claims["sub"]), email=claims.get("email"))


def require_role(role_name: str) -> Callable:
    async def dependency(user: CurrentUser = Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> CurrentUser:
        statement = select(UserRole).join(Role).where(UserRole.user_id == user.id, Role.name == role_name)
        if (await session.scalar(statement)) is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")
        return user
    return dependency


require_admin = require_role("admin")
