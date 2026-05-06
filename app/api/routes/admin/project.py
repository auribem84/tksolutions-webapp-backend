from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import uuid4

from app.api.deps import get_db, require_admin
from app.models.project import Project
from app.models.task import Task

router = APIRouter()


@router.post("/")
def create_project_with_tasks(
    data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    project = Project(
        id=uuid4(),
        name=data["name"],
        description=data.get("description"),
        status=data.get("status", "active"),
        start_date=data.get("start_date"),
        due_date=data.get("due_date"),
        organization_id=data["organization_id"],
    )

    db.add(project)
    db.flush()  # get project.id

    tasks = data.get("tasks", [])
    for t in tasks:
        if not t.get("title"):
            continue

        task = Task(
            id=uuid4(),
            title=t["title"],
            status=t.get("status", "todo"),
            assignee=t.get("assignee"),
            due_date=t.get("due_date"),
            project_id=project.id,
        )
        db.add(task)

    db.commit()

    return {"message": "Project created", "project_id": project.id}

@router.get("/with-tasks")
def list_projects_with_tasks(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    projects = db.query(Project).all()

    result = []
    for p in projects:
        tasks = db.query(Task).filter(Task.project_id == p.id).all()

        result.append({
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "status": p.status,
            "organization_id": str(p.organization_id),
            "tasks": [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "status": t.status,
                    "assignee": t.assignee,
                    "due_date": t.due_date,
                }
                for t in tasks
            ]
        })

    return result