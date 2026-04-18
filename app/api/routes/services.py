from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user, require_admin
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceOut

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "services router working"}


# ➕ CREATE (ADMIN)
@router.post("/", response_model=ServiceOut)
def create_service(
    data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    service = Service(
        name=data.name,
        organization_id=current_user["organization_id"],
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return service


# 📄 LIST (ORG)
@router.get("/", response_model=list[ServiceOut])
def list_services(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Service).filter(
        Service.organization_id == current_user["organization_id"]
    ).all()


# 🔍 GET ONE
@router.get("/{service_id}", response_model=ServiceOut)
def get_service(
    service_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.organization_id == current_user["organization_id"]
    ).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return service