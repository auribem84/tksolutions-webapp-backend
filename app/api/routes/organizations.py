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


# =========================
# BOOTSTRAP ORGANIZATION + FIRST ADMIN
# =========================
@router.post("/bootstrap")
def create_organization_with_admin(
    data: OrganizationBootstrapCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_default_admin),
):
    # 1. Create organization
    org = Organization(
        id=uuid.uuid4(),
        name=data.org_name,
    )
    db.add(org)
    db.flush()

    # 2. Create user (admin of new org)
    user = User(
        id=uuid.uuid4(),
        email=data.admin_email,
        hashed_password=hash_password(data.admin_password),
        is_active=True,
    )
    db.add(user)
    db.flush()

    # 3. Ensure admin role exists
    admin_role = db.query(Role).filter(Role.name == "admin").first()

    if not admin_role:
        admin_role = Role(
            id=uuid.uuid4(),
            name="admin"
        )
        db.add(admin_role)
        db.flush()

    # 4. Link user to organization
    link = OrganizationUser(
        user_id=user.id,
        organization_id=org.id,
        role_id=admin_role.id,
    )

    db.add(link)
    db.commit()

    return {
        "organization_id": org.id,
        "user_id": user.id,
        "message": "Organization bootstrap successful"
    }