import uuid
from sqlalchemy import Column, String, Date, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base

class ProjectStatus(str, enum.Enum):
    active = "active"
    on_hold = "on_hold"
    completed = "completed"
    archived = "archived"

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.active)

    start_date = Column(Date)
    due_date = Column(Date)

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))

    tasks = relationship("Task", back_populates="project", cascade="all, delete")