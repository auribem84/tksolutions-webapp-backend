from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TicketOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: str
    organization_id: UUID
    created_by: UUID

    class Config:
        from_attributes = True