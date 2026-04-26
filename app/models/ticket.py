from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ref = Column(String, unique=True, index=True)  # TK-001 público

    subject = Column(String, nullable=False)
    status = Column(String, default="open")
    priority = Column(String, default="medium")

    organization_id = Column(String, index=True)

    assignee = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    ticket_id = Column(String, ForeignKey("tickets.id"))
    sender = Column(String)
    text = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="messages")