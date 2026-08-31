from pydantic import BaseModel, Field, HttpUrl


class CreatorApplicationCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=160)
    phone_number: str = Field(min_length=3, max_length=50)
    social_profile_url: HttpUrl
    travel_experience: str = Field(min_length=1)
    portfolio: str = Field(min_length=1)
    sample_itinerary: str = Field(min_length=1)
    application_letter: str = Field(min_length=1)
    profile_photo_path: str = Field(min_length=1, max_length=500)
    id_document_path: str = Field(min_length=1, max_length=500)


class CreatorApplicationStatusResponse(BaseModel):
    status: str
