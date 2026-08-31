from fastapi import APIRouter

from app.api.v1 import admin, auth, creators, itineraries, purchases, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(creators.router)
api_router.include_router(itineraries.router)
api_router.include_router(purchases.router)
api_router.include_router(admin.router)
