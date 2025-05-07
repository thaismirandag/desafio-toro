from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str

class AuthResponse(BaseModel):
    token: str
    name: str

