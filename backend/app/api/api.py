from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.questions import router as questions_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")
router.include_router(questions_router)