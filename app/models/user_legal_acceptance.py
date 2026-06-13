import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class UserLegalAcceptance(Base):
    __tablename__ = "user_legal_acceptances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    document_type = Column(String(50), nullable=False)
    document_version = Column(String(20), nullable=False)
    accepted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
