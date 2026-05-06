from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.session import get_db
from app.api.deps import require_admin
from app.models.project import Project
from app.models.task import Task
from app.schemas.project import ProjectCreate, ProjectOut

router = APIRouter()


@router.post("/", response_model=ProjectOut)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    project = Project(
        id=uuid4(),
        name=data.name,
        description=data.description,
        status=data.status,
        start_date=data.start_date,
        due_date=data.due_date,
        organization_id=data.organization_id,
    )

    db.add(project)
    db.flush()  # importante para obtener project.id

    # ✅ crear tasks
    for t in data.tasks:
        task = Task(
            title=t.title,
            status=t.status,
            assignee=t.assignee,
            due_date=t.due_date,
            project_id=project.id,
        )
        db.add(task)

    db.commit()
    db.refresh(project)

    return project