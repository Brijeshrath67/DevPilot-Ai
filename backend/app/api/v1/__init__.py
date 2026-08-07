from app.api.v1.repos import router as repos_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(repos_router)
