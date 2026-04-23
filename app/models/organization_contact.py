from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base
from app.schemas.organization import OrganizationBootstrapCreate
import uuid

class OrganizationContact(Base):
    __tablename__ = "organization_contacts"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"))

    contact_name = Column(String(255))
    contact_lastname = Column(String(255))
    contact_title = Column(String(255))

    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    contact_mobile = Column(String(50))

    is_primary = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="contacts")