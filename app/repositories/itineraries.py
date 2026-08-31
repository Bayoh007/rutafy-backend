from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Itinerary, ItineraryStatus


async def get_owned_itinerary(session: AsyncSession, itinerary_id: UUID, creator_id: UUID) -> Itinerary | None:
    return await session.scalar(select(Itinerary).where(Itinerary.id == itinerary_id, Itinerary.creator_id == creator_id))


async def list_public_itineraries(session: AsyncSession, limit: int) -> list[Itinerary]:
    statement = select(Itinerary).where(Itinerary.status == ItineraryStatus.APPROVED).order_by(Itinerary.created_at.desc()).limit(limit)
    return list((await session.scalars(statement)).all())
