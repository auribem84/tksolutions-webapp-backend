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

    organization_id = Column(
        UUID,
        ForeignKey("organizations.id"),
        unique=True
    )

    itin = Column(String(50))

    # =========================================
    # ADDRESS
    # =========================================

    address1 = Column(String(255), nullable=True)
    address2 = Column(String(255), nullable=True)

    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip = Column(String(20), nullable=True)

    # =========================================
    # CONTACT
    # =========================================

    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)

    # =========================================
    # TIMESTAMPS
    # =========================================

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        nullable=True
    )

    # =========================================
    # RELATIONSHIPS
    # =========================================

    organization = relationship(
        "Organization",
        back_populates="profile"
    )