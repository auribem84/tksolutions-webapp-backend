from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.api.deps import get_db, require_admin, require_default_admin
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


@router.get("/{project_id}/tasks")
def get_project_tasks(
    project_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    return [
        {
            "id": str(t.id),
            "title": t.title,
            "status": t.status,
            "assignee": t.assignee,
            "due_date": str(t.due_date) if t.due_date else None,
        }
        for t in tasks
    ]


@router.patch("/tasks/{task_id}")
def update_task(
    task_id: str,
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if "status" in data:
        task.status = data["status"]

    db.commit()
    return {"message": "Task updated"}


@router.patch("/{project_id}")
def update_project(
    project_id: str,
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if "name" in data:
        project.name = data["name"]
    if "description" in data:
        project.description = data["description"]
    if "status" in data:
        project.status = data["status"]

    db.commit()
    return {"message": "Project updated"}


@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}