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

class OrganizationCreateFull(BaseModel):

    org_name: str

    itin: Optional[str] = None

    address1: Optional[str] = None
    address2: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

    phone: Optional[str] = None
    email: Optional[str] = None

    contacts: list[OrganizationContactCreate] = []

class OrganizationContactCreate(BaseModel):
    contact_name: str
    contact_lastname: Optional[str] = None
    contact_title: Optional[str] = None

    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_mobile: Optional[str] = None


class OrganizationBootstrapCreate(BaseModel):
    # =========================================
    # ORGANIZATION
    # =========================================

    org_name: str

    # =========================================
    # PROFILE
    # =========================================

    itin: Optional[str] = None

    address1: Optional[str] = None
    address2: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

    phone: Optional[str] = None
    email: Optional[str] = None

    # =========================================
    # ADMIN USER
    # =========================================

    admin_email: EmailStr
    admin_password: str
    admin_name: str

    # =========================================
    # CONTACTS
    # =========================================

    contacts: list[OrganizationContactCreate] = []

class OrganizationProfileOut(BaseModel):
    itin: Optional[str] = None

    # =========================================
    # ADDRESS
    # =========================================

    address1: Optional[str] = None
    address2: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

    # =========================================
    # CONTACT
    # =========================================

    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

class OrganizationProfileUpdate(BaseModel):
    itin: Optional[str] = None

    address1: Optional[str] = None
    address2: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None

    phone: Optional[str] = None
    email: Optional[str] = None

class OrganizationContactOut(BaseModel):
    contact_name: Optional[str]
    contact_lastname: Optional[str]
    contact_title: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    contact_mobile: Optional[str]

    class Config:
        from_attributes = True