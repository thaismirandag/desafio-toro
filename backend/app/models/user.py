from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, UUID4

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    pass

class UserInDB(UserBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True
