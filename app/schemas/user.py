from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    user_name: str
    user_lastname: str
    
class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=72)


class UserUpdate(UserBase):
    user_name: Optional[str] = None
    user_lastname: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class UserUpdateSelf(BaseModel):
    email: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    is_active: bool

    created_at: datetime
    created_by: Optional[UUID]

    modified_at: Optional[datetime]
    modified_by: Optional[UUID]

    # 👇 opcional pero MUY útil
    full_name: str

    class Config:
        orm_mode = True