from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))

    subtotal = Column(Float)
    tax_amount = Column(Float)
    discount_amount = Column(Float)
    total = Column(Float)

    status = Column(String, default="draft")