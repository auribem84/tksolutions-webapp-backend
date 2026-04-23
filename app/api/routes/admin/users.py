# app/api/routes/admin/users.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_default_admin
from app.models.user import User

router = APIRouter()

@router.get("/")
def list_users(db: Session = Depends(get_db), user=Depends(require_default_admin)):
    return db.query(User).all()


@router.patch("/{user_id}/status")
def toggle_user(user_id: str, is_active: bool, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    u = db.query(User).filter(User.id == user_id).first()

    if not u:
        return {"error": "not found"}

    u.is_active = is_active
    db.commit()

    return {"message": "updated"}