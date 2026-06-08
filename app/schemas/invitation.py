from pydantic import BaseModel, EmailStr
from datetime import datetime


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = "user"
    organization_id: str


class InvitationAccept(BaseModel):
    token: str
    user_name: str
    user_lastname: str
    password: str