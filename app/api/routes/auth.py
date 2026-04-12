from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import User
from app.models.organization_user import OrganizationUser
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter()
"""
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    print("LOGIN PAYLOAD:", data)
"""
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Get organization context
    org_user = db.query(OrganizationUser).filter(
        OrganizationUser.user_id == user.id
    ).first()

    if not org_user:
        raise HTTPException(status_code=400, detail="User not linked to organization")

    token = create_access_token({
        "user_id": str(user.id),
        "organization_id": str(org_user.organization_id),
        "role_id": str(org_user.role_id) if org_user.role_id else None
    })

    return {"access_token": token}

@router.get("/health")
def health():
    return {"status": "auth router working"}