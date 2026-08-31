from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ItineraryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    price_amount: int | None = Field(default=None, ge=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    is_free: bool = True

    @model_validator(mode="after")
    def validate_beta_price(self) -> "ItineraryCreate":
        if self.currency != "EUR":
            raise ValueError("Beta itinerary pricing must use EUR.")
        if self.is_free and self.price_amount not in (None, 0):
            raise ValueError("Free itineraries cannot have a positive price.")
        if not self.is_free and not self.price_amount:
            raise ValueError("A future-price itinerary needs a positive price amount.")
        return self


class ItineraryResponse(BaseModel):
    id: UUID
    title: str
    status: str
    price_amount: int | None
    currency: str
    is_free: bool
