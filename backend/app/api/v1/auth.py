from fastapi import APIRouter, HTTPException, Request
from fastapi.security import HTTPBearer

from app.models.user import AuthResponse, UserCreate
from app.services.auth import AuthService

router = APIRouter()
auth_service = AuthService()

security = HTTPBearer(auto_error=False)

async def get_current_user(request: Request):
    print("Iniciando autenticação...")
    auth_header = request.headers.get("Authorization")
    print(f"Header de autorização recebido: {auth_header}")
    
    if not auth_header:
        print("Erro: Token não fornecido")
        raise HTTPException(status_code=401, detail="Token não fornecido")

    if not auth_header.startswith("Bearer "):
        print("Erro: Formato do token inválido")
        raise HTTPException(status_code=401, detail="Formato do token inválido")
    
    token = auth_header.split(" ", 1)[1]
    print(f"Token extraído: {token}")
    
    user = await auth_service.get_user_by_session(token)
    print(f"Usuário encontrado: {user}")
    
    if not user:
        print("Erro: Token inválido ou expirado")
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    return user

@router.post("/login", response_model=AuthResponse)
async def login(user: UserCreate):
    token = await auth_service.login(user.name)
    return AuthResponse(token=token, name=user.name)