# app/api/routes/admin/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_default_admin
from app.models.user import User

router = APIRouter()

@router.get("/")
def list_users(db: Session = Depends(get_db), user=Depends(require_default_admin)):
    return db.query(User).all()


@router.patch("/{user_id}")
def update_user(user_id: str, data: dict, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    u = db.query(User).filter(User.id == user_id).first()

    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    if "user_name" in data:
        u.user_name = data["user_name"]
    if "user_lastname" in data:
        u.user_lastname = data["user_lastname"]
    if "is_active" in data:
        u.is_active = data["is_active"]

    db.commit()
    return {"message": "User updated"}


@router.patch("/{user_id}/status")
def toggle_user(user_id: str, is_active: bool, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    u = db.query(User).filter(User.id == user_id).first()

    if not u:
        return {"error": "not found"}

    u.is_active = is_active
    db.commit()

    return {"message": "updated"}