from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class OrganizationCreate(BaseModel):
    name: str


class OrganizationOut(BaseModel):
    id: UUID
    name: str
    status: str

    class Config:
        from_attributes = True

class OrganizationBootstrapCreate(BaseModel):
    org_name: str
    admin_email: EmailStr
    admin_password: str
    admin_name: str

class OrganizationProfileOut(BaseModel):
    itin: Optional[str] = None

    class Config:
        from_attributes = True

class OrganizationContactOut(BaseModel):
    contact_name: Optional[str]
    contact_lastname: Optional[str]
    contact_title: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    contact_mobile: Optional[str]

    class Config:
        from_attributes = True