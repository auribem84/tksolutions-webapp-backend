# app/api/routes/admin/organizations.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, require_default_admin
from app.models.organization import Organization

router = APIRouter()

@router.post("/")
def create_organization(data: dict, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    org = Organization(name=data["name"])
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/")
def list_organizations(db: Session = Depends(get_db), user=Depends(require_default_admin)):
    return db.query(Organization).all()


@router.get("/{org_id}")
def get_organization(org_id: UUID, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Not found")
    return org


@router.put("/{org_id}")
def update_organization(org_id: UUID, data: dict, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org:
        raise HTTPException(404, "Not found")

    org.name = data.get("name", org.name)
    db.commit()
    return {"message": "updated"}


@router.delete("/{org_id}")
def deactivate_organization(org_id: UUID, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org:
        raise HTTPException(404, "Not found")

    org.is_active = False
    db.commit()
    return {"message": "deactivated"}