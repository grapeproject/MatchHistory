from fastapi import APIRouter
from .summoner import router as summoner_router
# router 생성
V1 = APIRouter(prefix="/api/v1")

V1.include_router(summoner_router)
