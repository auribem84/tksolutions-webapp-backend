from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class BillingCreate(BaseModel):
    description: str
    amount: float


class BillingOut(BaseModel):
    id: UUID
    description: Optional [str]
    amount: float
    status: str
    organization_id: UUID

    class Config:
        from_attributes = True