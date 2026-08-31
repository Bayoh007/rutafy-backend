from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CreatorProfile, CreatorStatus, Itinerary, ItineraryStatus
from app.schemas.itinerary import ItineraryCreate
from app.schemas.common import CurrentUser


class CreatorNotVerifiedError(Exception):
    pass


async def create_draft(session: AsyncSession, user: CurrentUser, payload: ItineraryCreate) -> Itinerary:
    creator = await session.get(CreatorProfile, user.id)
    if creator is None or creator.status not in {CreatorStatus.VERIFIED, CreatorStatus.PREMIUM}:
        raise CreatorNotVerifiedError
    itinerary = Itinerary(
        creator_id=user.id,
        title=payload.title,
        status=ItineraryStatus.DRAFT,
        price_amount=payload.price_amount,
        currency=payload.currency,
        is_free=payload.is_free,
    )
    session.add(itinerary)
    await session.commit()
    await session.refresh(itinerary)
    return itinerary
