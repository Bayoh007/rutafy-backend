from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import get_current_user
from app.repositories.itineraries import list_public_itineraries
from app.schemas.common import CurrentUser
from app.schemas.itinerary import ItineraryCreate, ItineraryResponse
from app.services.itineraries import CreatorNotVerifiedError, create_draft

router = APIRouter(prefix="/itineraries", tags=["itineraries"])


def to_response(item: object) -> ItineraryResponse:
    return ItineraryResponse.model_validate(item, from_attributes=True)


@router.get("", response_model=list[ItineraryResponse])
async def discover_itineraries(limit: int = Query(default=20, ge=1, le=100), session: AsyncSession = Depends(get_db_session)) -> list[ItineraryResponse]:
    return [to_response(item) for item in await list_public_itineraries(session, limit)]


@router.post("", response_model=ItineraryResponse, status_code=status.HTTP_201_CREATED)
async def create_itinerary(payload: ItineraryCreate, current_user: CurrentUser = Depends(get_current_user), session: AsyncSession = Depends(get_db_session)) -> ItineraryResponse:
    try:
        return to_response(await create_draft(session, current_user, payload))
    except CreatorNotVerifiedError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only verified creators can create itineraries.") from error
