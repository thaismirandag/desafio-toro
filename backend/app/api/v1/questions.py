from fastapi import APIRouter, Request

from app.api.v1.auth import get_current_user
from app.models.question import QuestionCreate, QuestionResponse
from app.services.question import QuestionService

router = APIRouter(prefix="/questions", tags=["questions"])
question_service = QuestionService()

@router.post("", response_model=QuestionResponse)
async def create_question(
    request: Request,
    question: QuestionCreate
):
    print("Recebendo requisição POST /questions")
    print(f"Question data: {question.dict()}")
    
    print("Obtendo usuário atual...")
    session = await get_current_user(request)
    print(f"Sessão obtida: {session}")
    
    print(f"Chamando create_question com question={question.question} e session_id={session['session_id']}")
    try:
        response = await question_service.create_question(
            question.question, 
            session['session_id']
        )
        print(f"Resposta do create_question: {response.dict()}")
        return response
    except Exception as e:
        print(f"Erro ao criar questão: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        raise
