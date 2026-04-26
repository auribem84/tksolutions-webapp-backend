from pydantic import BaseModel
from typing import List
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