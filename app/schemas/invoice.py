from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class InvoiceCreate(BaseModel):
    organization_id: UUID
    amount: float
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class InvoiceOut(BaseModel):
    id: UUID
    organization_id: UUID
    amount: float
    description: Optional[str]
    status: str
    due_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True