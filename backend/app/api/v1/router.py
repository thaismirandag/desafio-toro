from fastapi import APIRouter, HTTPException, Depends
from app.services.question import QuestionService
from app.models.question import QuestionCreate, QuestionResponse
from typing import List
from app.api.v1.auth import get_current_user
from app.models.user import UserResponse

router = APIRouter(tags=["questions"])
question_service = QuestionService()

@router.post("/questions", response_model=QuestionResponse)
async def create_question(
    question: QuestionCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    return await question_service.create_question(question.question, current_user.id)


@router.get("/questions", response_model=List[QuestionResponse])
async def list_questions(
    current_user: UserResponse = Depends(get_current_user)
):
    return await question_service.list_questions(current_user.id) 