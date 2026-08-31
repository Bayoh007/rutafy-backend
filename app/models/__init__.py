"""SQLAlchemy mappings for Rutafy beta.

Sensitive creator application records live in the private schema and are never
serialized by public API schemas.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CreatorStatus(str, enum.Enum):
    NONE = "none"
    PENDING = "pending"
    VERIFIED = "verified"
    PREMIUM = "premium"


class ItineraryStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Profile(Timestamped, Base):
    __tablename__ = "profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    display_name: Mapped[str | None] = mapped_column(String(120))
    avatar_path: Mapped[str | None] = mapped_column(String(500))


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)


class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)


class CreatorProfile(Timestamped, Base):
    __tablename__ = "creator_profiles"
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    status: Mapped[CreatorStatus] = mapped_column(Enum(CreatorStatus, name="creator_status"), default=CreatorStatus.NONE, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)
    public_photo_path: Mapped[str | None] = mapped_column(String(500))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Itinerary(Timestamped, Base):
    __tablename__ = "itineraries"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("creator_profiles.user_id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(220), unique=True)
    status: Mapped[ItineraryStatus] = mapped_column(Enum(ItineraryStatus, name="itinerary_status"), default=ItineraryStatus.DRAFT, nullable=False, index=True)
    price_amount: Mapped[int | None] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    approved_version_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))


class ItineraryVersion(Timestamped, Base):
    __tablename__ = "itinerary_versions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    __table_args__ = (UniqueConstraint("itinerary_id", "version_number", name="uq_itinerary_version_number"),)


class CreatorFollow(Base):
    __tablename__ = "creator_follows"
    follower_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    creator_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("creator_profiles.user_id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ItineraryFollow(Base):
    __tablename__ = "itinerary_follows"
    follower_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    itinerary_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Collection(Timestamped, Base):
    __tablename__ = "collections"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class CollectionItinerary(Base):
    __tablename__ = "collection_itineraries"
    collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True)
    itinerary_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CreatorApplication(Timestamped, Base):
    __tablename__ = "creator_applications"
    __table_args__ = {"schema": "private"}
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applicant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus, name="creator_application_status", schema="private"), default=ApplicationStatus.PENDING, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=False)
    social_profile_url: Mapped[str] = mapped_column(String(500), nullable=False)
    travel_experience: Mapped[str] = mapped_column(Text, nullable=False)
    portfolio: Mapped[str] = mapped_column(Text, nullable=False)
    sample_itinerary: Mapped[str] = mapped_column(Text, nullable=False)
    application_letter: Mapped[str] = mapped_column(Text, nullable=False)
    profile_photo_path: Mapped[str] = mapped_column(String(500), nullable=False)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_note: Mapped[str | None] = mapped_column(Text)


class CreatorApplicationDocument(Base):
    __tablename__ = "creator_application_documents"
    __table_args__ = {"schema": "private"}
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("private.creator_applications.id", ondelete="CASCADE"), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    document_type: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
