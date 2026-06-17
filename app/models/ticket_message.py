import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ticket_id = Column(UUID(as_uuid=True), nullable=False)

    sender = Column(String)
    text = Column(Text, nullable=False)
    source = Column(String, nullable=False, default="app")
    sender_phone = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)