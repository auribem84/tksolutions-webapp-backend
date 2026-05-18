from sqlalchemy import Column, String, ForeignKey, Float, DateTime, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)

    status = Column(String, default="pending")
    due_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization")