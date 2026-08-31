import pytest
from pydantic import ValidationError

from app.schemas.itinerary import ItineraryCreate


def test_paid_beta_itinerary_requires_eur_price() -> None:
    payload = ItineraryCreate(title="Weekend in Freetown", is_free=False, price_amount=1500)
    assert payload.currency == "EUR"


def test_free_itinerary_cannot_have_price() -> None:
    with pytest.raises(ValidationError):
        ItineraryCreate(title="Weekend in Freetown", is_free=True, price_amount=1500)


def test_non_eur_beta_price_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ItineraryCreate(title="Weekend in Freetown", is_free=False, price_amount=1500, currency="USD")
