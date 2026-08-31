from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ApplicationStatus, CreatorApplication, CreatorApplicationDocument, CreatorProfile, CreatorStatus
from app.schemas.creator import CreatorApplicationCreate
from app.schemas.common import CurrentUser


async def submit_application(session: AsyncSession, user: CurrentUser, payload: CreatorApplicationCreate) -> CreatorApplication:
    creator = await session.get(CreatorProfile, user.id)
    if creator is None:
        creator = CreatorProfile(user_id=user.id, status=CreatorStatus.PENDING)
        session.add(creator)
    else:
        creator.status = CreatorStatus.PENDING
    application = CreatorApplication(
        applicant_id=user.id,
        status=ApplicationStatus.PENDING,
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        social_profile_url=str(payload.social_profile_url),
        travel_experience=payload.travel_experience,
        portfolio=payload.portfolio,
        sample_itinerary=payload.sample_itinerary,
        application_letter=payload.application_letter,
        profile_photo_path=payload.profile_photo_path,
    )
    session.add(application)
    await session.flush()
    session.add(CreatorApplicationDocument(application_id=application.id, storage_path=payload.id_document_path, document_type="identity"))
    await session.commit()
    await session.refresh(application)
    return application
