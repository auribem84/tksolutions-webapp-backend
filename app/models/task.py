import uuid
from sqlalchemy import Column, String, Date, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base

class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    blocked = "blocked"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo)

    due_date = Column(Date)
    assignee = Column(String)

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))

    project = relationship("Project", back_populates="tasks")