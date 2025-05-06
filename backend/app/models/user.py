from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, UUID4

class UserCreate(BaseModel):
    name: str

class AuthResponse(BaseModel):
    token: str
    name: str

