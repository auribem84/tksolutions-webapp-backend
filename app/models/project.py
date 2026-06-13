import uuid
from sqlalchemy import Column, String, Date, ForeignKey, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base

class ProjectStatus(str, enum.Enum):
    planning = "planning"
    in_progress = "in_progress"
    in_review = "in_review"
    on_hold = "on_hold"
    completed = "completed"
    support = "support"
    cancelled = "cancelled"
    archived = "archived"

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_tag = Column(String(12), unique=True, nullable=True)
    name = Column(String, nullable=False)
    description = Column(String)
    notes = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.planning)

    start_date = Column(Date)
    due_date = Column(Date)

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))

    tasks = relationship("Task", back_populates="project", cascade="all, delete")