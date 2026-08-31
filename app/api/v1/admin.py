from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.auth import require_admin
from app.models import ApplicationStatus, CreatorApplication, CreatorProfile, CreatorStatus, Itinerary, ItineraryStatus
from app.schemas.common import CurrentUser, Message

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/creator-applications/{application_id}/approve", response_model=Message)
async def approve_creator_application(application_id: UUID, admin: CurrentUser = Depends(require_admin), session: AsyncSession = Depends(get_db_session)) -> Message:
    application = await session.get(CreatorApplication, application_id)
    if application is None or application.status is not ApplicationStatus.PENDING:
        raise HTTPException(status_code=404, detail="Pending creator application not found.")
    application.status = ApplicationStatus.APPROVED
    application.reviewed_by, application.reviewed_at = admin.id, datetime.now(timezone.utc)
    creator = await session.get(CreatorProfile, application.applicant_id)
    if creator is None:
        creator = CreatorProfile(user_id=application.applicant_id)
        session.add(creator)
    creator.status, creator.verified_at = CreatorStatus.VERIFIED, datetime.now(timezone.utc)
    await session.commit()
    return Message(detail="Creator application approved.")


@router.post("/itineraries/{itinerary_id}/approve", response_model=Message)
async def approve_itinerary(itinerary_id: UUID, _: CurrentUser = Depends(require_admin), session: AsyncSession = Depends(get_db_session)) -> Message:
    itinerary = await session.get(Itinerary, itinerary_id)
    if itinerary is None or itinerary.status is not ItineraryStatus.PENDING_REVIEW:
        raise HTTPException(status_code=404, detail="Pending itinerary not found.")
    itinerary.status = ItineraryStatus.APPROVED
    await session.commit()
    return Message(detail="Itinerary approved.")
