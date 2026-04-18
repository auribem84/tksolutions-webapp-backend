from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class ServiceCreate(BaseModel):
    name: str


class ServiceOut(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: Optional[str]
    status: str
    plan: Optional[str]
    monthly_fee: Optional[str]
    last_activity: Optional[str]