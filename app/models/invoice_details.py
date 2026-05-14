from sqlalchemy import Column, String, ForeignKey, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


class InvoiceDetail(Base):
    __tablename__ = "invoice_details"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4   # 👈 CAMBIO IMPORTANTE
    )

    invoice_id = Column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String(255), nullable=False)

    description = Column(Text)

    quantity = Column(Integer, default=1)

    unit_price = Column(Float, nullable=False)

    total = Column(Float, nullable=False)