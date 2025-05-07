from fastapi import APIRouter, Request
from app.api.v1.auth import get_current_user
from app.models.question import QuestionCreate, QuestionResponse
from app.services.question import QuestionService
from typing import List

router = APIRouter(prefix="/questions", tags=["questions"])
question_service = QuestionService()

@router.post("", response_model=QuestionResponse)
async def create_question(
    request: Request,
    question: QuestionCreate
):

    session = await get_current_user(request)
    print(f"Sessão obtida: {session}")
    
    try:
        response = await question_service.create_question(
            question.question, 
            session['session_id']
        )
        return response
    except Exception as e:
        print(f"Erro ao criar questão: {str(e)}")
        raise

@router.get("/{session_id}", response_model=List[QuestionResponse])
async def list_questions(
    session_id: str
):

    try:
        questions = await question_service.list_questions(session_id)
        return questions
    except Exception as e:
        print(f"Erro ao listar questões: {str(e)}")
        raise