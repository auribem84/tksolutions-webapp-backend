from pydantic import BaseModel, EmailStr
from uuid import UUID


class OrganizationCreate(BaseModel):
    name: str


class OrganizationOut(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class OrganizationBootstrapCreate(BaseModel):
    org_name: str
    admin_email: EmailStr
    admin_password: str
    admin_name: str