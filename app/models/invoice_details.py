from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


class InvoiceDetail(Base):
    __tablename__ = "invoice_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"))

    title = Column(String(255), nullable=False)
    description = Column(Text)

    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(12, 2))

    created_at = Column(DateTime, default=datetime.utcnow)