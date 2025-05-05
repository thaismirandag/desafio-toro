from fastapi import APIRouter
from app.api.v1.router import router as v1_router
from app.api.v1.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(v1_router) 