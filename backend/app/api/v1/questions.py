from fastapi import APIRouter, HTTPException, Depends
from app.services.question import QuestionService
from app.models.question import QuestionCreate, QuestionResponse
from typing import List
from app.api.v1.auth import get_current_user 

router = APIRouter(prefix="/questions", tags=["questions"])
question_service = QuestionService()

@router.post("", response_model=QuestionResponse)
async def create_question(
    question: QuestionCreate,
    user_name: str = Depends(get_current_user)
):
    return await question_service.create_question(question.question, user_name)

@router.get("", response_model=List[QuestionResponse])
async def list_questions(user_name: str = Depends(get_current_user)):
    return await question_service.list_questions(user_name)
