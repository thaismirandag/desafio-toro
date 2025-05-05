from datetime import datetime, timedelta
import uuid
from typing import Optional, Dict
from app.models.user import UserCreate, UserResponse, UserInDB

USERS: Dict[str, UserInDB] = {}
SESSIONS: Dict[str, dict] = {}

class AuthService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
    
    async def signup(self, user_data: UserCreate) -> UserResponse:
        print(f"Criando novo usuário: {user_data.email}")
        user_id = str(uuid.uuid4())
        user = UserInDB(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            created_at=datetime.utcnow()
        )
        USERS[user_id] = user
        print(f"Usuário criado com ID: {user_id}")
        print(f"Usuários armazenados: {USERS}")
        return UserResponse.model_validate(user)
    
    async def login(self, email: str) -> Optional[str]:
        print(f"Tentando login para email: {email}")
        user = next((u for u in USERS.values() if u.email == email), None)
        if not user:
            print(f"Usuário não encontrado: {email}")
            return None
        
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {
            'user_id': str(user.id),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        print(f"Sessão criada com ID: {session_id}")
        print(f"Sessões armazenadas: {SESSIONS}")
        return session_id
    
    async def get_user_by_session(self, session_id: str) -> Optional[UserResponse]:
        try:
            print(f"Buscando sessão: {session_id}")
            print(f"Sessões disponíveis: {SESSIONS}")
            
            session = SESSIONS.get(session_id)
            if not session:
                print(f"Sessão não encontrada: {session_id}")
                return None
            
            expires_at = datetime.fromisoformat(session['expires_at'])
            if expires_at < datetime.utcnow():
                print(f"Sessão expirada: {session_id}")
                print(f"Expiração: {expires_at}, Agora: {datetime.utcnow()}")
                del SESSIONS[session_id]
                return None
            
            user_id = session['user_id']
            print(f"Buscando usuário com ID: {user_id}")
            print(f"Usuários disponíveis: {USERS}")
            
            user = USERS.get(user_id)
            if user:
                print(f"Usuário encontrado: {user.email}")
                return UserResponse.model_validate(user)
            
            print(f"Usuário não encontrado para sessão: {session_id}")
            return None
        except Exception as e:
            print(f"Erro ao validar sessão: {str(e)}")
            return None 