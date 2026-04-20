from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_user import OrganizationUser
from app.models.role import Role
from app.schemas.user import UserOut, UserUpdateSelf

router = APIRouter()


# 👤 Ver perfil propio
@router.get("/me", response_model=UserOut)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ✏️ Update perfil propio
@router.put("/me", response_model=UserOut)
def update_my_profile(
    data: UserUpdateSelf,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.email:
        user.email = data.email

    db.commit()
    db.refresh(user)

    return user


# 🔐 helper admin check
def require_admin(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user


# 📄 listar usuarios de la org
@router.get("/users", response_model=list[UserOut])
def list_org_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    users = db.query(User).filter(
        User.organization_id == current_user["organization_id"]
    ).all()

    return users


# 🚫 activar/desactivar usuario
@router.patch("/users/{user_id}/status")
def toggle_user_status(
    user_id: UUID,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == current_user["organization_id"]
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = is_active

    db.commit()

    return {"message": "User status updated"}

@router.get("/team")
def get_team(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    org_id = current_user["organization_id"]

    results = (
        db.query(User, OrganizationUser, Role)
        .join(OrganizationUser, User.id == OrganizationUser.user_id)
        .join(Role, Role.id == OrganizationUser.role_id)
        .filter(OrganizationUser.organization_id == org_id)
        .all()
    )

    return [
        {
            "id": u.id,
            "name": f"{u.first_name} {u.last_name}" if hasattr(u, "first_name") else u.email,
            "email": u.email,
            "role": r.name,
            "status": "active",
            "last_login": "2 hours ago",
        }
        for u, ou, r in results
    ]

@router.get("/organization")
def get_organization(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    org_id = current_user["organization_id"]

    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return {
        "id": org.id,
        "name": org.name,
    }