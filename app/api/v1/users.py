from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.common import CurrentUser

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=CurrentUser)
async def get_me(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return current_user
