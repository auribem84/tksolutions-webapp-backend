from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class InvoiceDetailCreate(BaseModel):
    title: str
    description: Optional[str] = None
    quantity: int = 1
    unit_price: float

class InvoiceCreate(BaseModel):
    organization_id: UUID
    items: List[InvoiceDetailCreate]