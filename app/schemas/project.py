from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import date

class TaskOut(BaseModel):
    id: UUID
    title: str
    status: str
    assignee: str | None
    due_date: date | None

    class Config:
        from_attributes = True


class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: str
    status: str
    start_date: date | None
    due_date: date | None
    progress: int
    tasks: List[TaskOut]

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    assignee: Optional[str] = None
    due_date: Optional[date] = None

class ProjectWithTasksCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    organization_id: str
    tasks: List[TaskCreate] = []

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str]
    status: str
    start_date: Optional[date]
    due_date: Optional[date]
    organization_id: UUID
    tasks: List[TaskCreate]