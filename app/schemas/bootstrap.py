from pydantic import BaseModel, EmailStr
from typing import Optional


class BootstrapRequest(BaseModel):
    org_name: str
    org_contact_email: Optional[EmailStr] = None
    org_contact_phone: Optional[str] = None
    org_address: Optional[str] = None

    admin_email: EmailStr
    admin_role: str = "admin"