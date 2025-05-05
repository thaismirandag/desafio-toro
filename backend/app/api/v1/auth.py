from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import UserCreate, UserResponse
from app.services.auth import AuthService
from typing import Optional

router = APIRouter(tags=["auth"])
auth_service = AuthService()
security = HTTPBearer()

class AuthResponse(UserResponse):
    token: str

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    try:
        token = credentials.credentials
        if token.startswith('Bearer '):
            token = token[7:]
        
        print(f"Validando token: {token}")
        user = await auth_service.get_user_by_session(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado"
            )
        return user
    except Exception as e:
        print(f"Erro ao validar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )

@router.post("/login", response_model=AuthResponse)
async def login(user_data: UserCreate):
    print(f"Tentando login com email: {user_data.email}")
    token = await auth_service.login(user_data.email)
    user = None
    
    if not token:
        print(f"Usuário não encontrado, criando novo usuário: {user_data.email}")
        user = await auth_service.signup(user_data)
        token = await auth_service.login(user.email)
    
    if not user:
        print(f"Buscando usuário pelo token: {token}")
        user = await auth_service.get_user_by_session(token)
        if not user:
            raise HTTPException(status_code=500, detail="Erro ao autenticar usuário")
    
    print(f"Login bem sucedido para: {user.email}")
    return AuthResponse(
        token=token,
        **user.model_dump()
    )