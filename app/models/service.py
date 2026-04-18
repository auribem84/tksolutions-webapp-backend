from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from datetime import datetime

class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text)

    status = Column(String(255), nullable=False)

    plan = Column(String(255), nullable=True)
    monthly_fee = Column(String(255), nullable=True)
    last_activity = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)