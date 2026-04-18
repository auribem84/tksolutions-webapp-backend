from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
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