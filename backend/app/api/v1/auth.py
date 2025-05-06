from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.services.auth import AuthService
from app.models.user import AuthResponse, UserCreate

router = APIRouter()
auth_service = AuthService()

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_name = await AuthService().get_user_by_session(token)
    
    if not user_name:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user_name

@router.post("/login", response_model=AuthResponse)
async def login(user: UserCreate):
    token = await auth_service.login(user.name)
    return AuthResponse(token=token, name=user.name)