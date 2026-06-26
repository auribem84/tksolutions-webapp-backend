from sqlalchemy import Column, String, ForeignKey, Boolean, Integer, DateTime, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.base import Base


class RecurringInvoice(Base):
    __tablename__ = "recurring_invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    description = Column(Text, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    frequency = Column(String, default="monthly")  # monthly, quarterly, annually
    day_of_month = Column(Integer, default=1)       # 1–28, used for monthly billing

    start_date = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization")
