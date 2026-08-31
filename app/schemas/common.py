from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    detail: str


class CurrentUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str | None = None
