from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from app.db.base import Base
from app.schemas.organization import OrganizationBootstrapCreate
import uuid

class OrganizationProfile(Base):
    __tablename__ = "organization_profiles"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"), unique=True)

    itin = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="profile")