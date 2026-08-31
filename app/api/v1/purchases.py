"""Reserved integration boundary for future individual itinerary purchases.

Beta deliberately exposes no purchase, checkout, payment, refund, or payout API.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/purchases", tags=["purchases"])
