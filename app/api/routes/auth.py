from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import os

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.models.role import Role
from app.models.organization_user import OrganizationUser
from app.core.security import verify_password, create_access_token, hash_password
from app.schemas.auth import LoginRequest, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.services.email_service import send_password_reset_email

RESET_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

    # 1. Buscar usuario global
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. Obtener organización activa del usuario
    org_user = db.query(OrganizationUser).filter(
        OrganizationUser.user_id == user.id
    ).first()

    if not org_user:
        raise HTTPException(status_code=400, detail="User not linked to organization")

    print("TOKEN PAYLOAD:", {
        "user_id": str(user.id),
        "organization_id": str(org_user.organization_id),
    })

    # 3. Crear JWT multi-tenant
    token = create_access_token({
        "user_id": str(user.id),
        "organization_id": str(org_user.organization_id),
        "role_id": str(org_user.role_id)
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/forgot-password", status_code=200)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    # Always return 200 to avoid leaking whether the email exists
    if not user or not user.is_active:
        return {"message": "If that email is registered you will receive a reset link shortly."}

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    db.commit()

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_url}/reset-password?token={token}"

    send_password_reset_email(user.email, reset_link)

    return {"message": "If that email is registered you will receive a reset link shortly."}


@router.post("/reset-password", status_code=200)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == data.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    if not user.reset_token_expires_at or datetime.utcnow() > user.reset_token_expires_at:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    if len(data.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters.")

    user.hashed_password = hash_password(data.password)
    user.reset_token = None
    user.reset_token_expires_at = None
    user.modified_at = datetime.utcnow()
    db.commit()

    return {"message": "Password reset successfully."}


@router.get("/me")
def get_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    org = db.query(Organization).filter(Organization.id == current_user["organization_id"]).first()

    default_org_id = os.getenv("DEFAULT_ORG_ID")

    is_default_org_admin = (
        str(current_user["organization_id"]) == str(default_org_id)
        and current_user.get("role") == "admin"
    )

    return {
        "email": user.email,
        "role": current_user.get("role", "User"),
        "organization_id": org.id,
        "organization": org.name if org else None,
        "user_name": user.user_name,
        "user_lastname": user.user_lastname,
        "full_name": f"{user.user_name} {user.user_lastname}",
        "is_default_org_admin": is_default_org_admin
    }