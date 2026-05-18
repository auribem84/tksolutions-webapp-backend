from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from passlib.hash import bcrypt

from app.api.deps import get_db, require_default_admin

from app.models.organization import Organization
from app.models.organization_user import OrganizationUser
from app.schemas.organization_users import OrgUserCreate
from app.models.user import User
from app.models.role import Role

router = APIRouter()


# =========================================
# GET USERS BY ORGANIZATION
# =========================================
@router.get("/{org_id}/users")
def get_organization_users(
    org_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):

    organization = db.query(Organization).filter(
        Organization.id == org_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    org_users = db.query(OrganizationUser).filter(
        OrganizationUser.organization_id == org_id
    ).all()

    results = []

    for item in org_users:

        db_user = db.query(User).filter(
            User.id == item.user_id
        ).first()

        role = db.query(Role).filter(
            Role.id == item.role_id
        ).first()

        if not db_user:
            continue

        results.append({
            "id": str(db_user.id),
            "email": db_user.email,
            "full_name": getattr(db_user, "full_name", ""),
            "role": role.name if role else None,
        })

    return results

@router.post("/organizations/{org_id}/users")
def create_org_user(
    org_id: str,
    payload: OrgUserCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_default_admin),
):

    # 1. create user
    user = User(
        id=uuid4(),
        name=payload.name,
        email=payload.email,
        hashed_password=bcrypt.hash(payload.password),
    )

    db.add(user)
    db.flush()

    # 2. link to org
    org_user = OrganizationUser(
        id=uuid4(),
        user_id=user.id,
        organization_id=org_id,
        role_id=payload.role_id
    )

    db.add(org_user)
    db.commit()

    return {"message": "User created"}