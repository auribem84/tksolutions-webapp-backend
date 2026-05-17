from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.api.deps import get_db, require_default_admin
from app.models.organization import Organization
from app.models.user import User
from app.models.organization_user import OrganizationUser
from app.models.role import Role

from app.schemas.organization import (
    OrganizationCreate,
    OrganizationOut,
    OrganizationBootstrapCreate,
)

from app.models.organization_profile import OrganizationProfile
from app.models.organization_contact import OrganizationContact

from app.core.security import hash_password

router = APIRouter()


# =========================
# CREATE ORGANIZATION (ONLY DEFAULT ADMIN)
# =========================
@router.post("/", response_model=OrganizationOut)
def create_org(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_default_admin),
):
    org = Organization(
        id=uuid.uuid4(),
        name=data.name
    )

    db.add(org)
    db.commit()
    db.refresh(org)

    return org


# =========================
# LIST ORGANIZATIONS
# =========================
@router.get("/", response_model=list[OrganizationOut])
def list_orgs(
    db: Session = Depends(get_db),
    current_user=Depends(require_default_admin),
):
    return db.query(Organization).all()


