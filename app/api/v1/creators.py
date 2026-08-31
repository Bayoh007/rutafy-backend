from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import get_current_user
from app.schemas.common import CurrentUser
from app.schemas.creator import CreatorApplicationCreate, CreatorApplicationStatusResponse
from app.services.creators import submit_application

router = APIRouter(prefix="/creators", tags=["creators"])


@router.post("/application", response_model=CreatorApplicationStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: CreatorApplicationCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CreatorApplicationStatusResponse:
    application = await submit_application(session, current_user, payload)
    return CreatorApplicationStatusResponse(status=application.status.value)
