from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base
from app.schemas.organization import OrganizationBootstrapCreate
import uuid

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, server_default=func.now())

    profile = relationship("OrganizationProfile", back_populates="organization", uselist=False)
    contacts = relationship("OrganizationContact", back_populates="organization")