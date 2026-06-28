from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.api.deps import get_db, require_default_admin
from app.models.service import Service

router = APIRouter()


@router.post("")
def create_service(
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    service = Service(
        id=uuid4(),
        organization_id=data["organization_id"],
        name=data["name"],
        description=data.get("description"),
        status=data.get("status", "active"),
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return {"message": "Service created", "service_id": str(service.id)}


@router.patch("/{service_id}")
def update_service(
    service_id: str,
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if "name" in data:
        service.name = data["name"]
    if "description" in data:
        service.description = data["description"]
    if "status" in data:
        service.status = data["status"]

    db.commit()
    return {"message": "Service updated"}


@router.delete("/{service_id}")
def delete_service(
    service_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    db.delete(service)
    db.commit()
    return {"message": "Service deleted"}
