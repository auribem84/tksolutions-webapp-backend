from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class OrganizationUser(Base):
    __tablename__ = "organization_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))

    role = relationship("Role")
    user = relationship("User")
    organization = relationship("Organization")