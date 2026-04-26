from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.project import Project
from app.schemas.project import ProjectOut

router = APIRouter()


def calculate_progress(tasks):
    if not tasks:
        return 0
    done = len([t for t in tasks if t.status == "done"])
    return int((done / len(tasks)) * 100)


# 📄 LIST PROJECTS (ORG)
@router.get("/", response_model=list[ProjectOut])
def get_projects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    projects = db.query(Project).filter(
        Project.organization_id == current_user["organization_id"]
    ).all()

    result = []
    for p in projects:
        progress = calculate_progress(p.tasks)

        result.append({
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "status": p.status,
            "start_date": p.start_date,
            "due_date": p.due_date,
            "progress": progress,
            "tasks": [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "status": t.status,
                    "assignee": t.assignee,
                    "due_date": t.due_date,
                }
                for t in p.tasks
            ],
        })

    return result