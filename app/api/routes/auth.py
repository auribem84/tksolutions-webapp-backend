from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.user import User
from app.models.organization_user import OrganizationUser
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse

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