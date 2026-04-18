from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.models.organization_user import OrganizationUser
from app.models.role import Role
from app.core.security import SECRET_KEY, ALGORITHM

security = HTTPBearer()


# =========================
# DB
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# CURRENT USER (DICT SIMPLE Y ESTABLE)
# =========================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        organization_id = payload.get("organization_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not user_id or not organization_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    org_user = db.query(OrganizationUser).filter(
        OrganizationUser.user_id == user_id,
        OrganizationUser.organization_id == organization_id
    ).first()

    if not org_user:
        raise HTTPException(status_code=403, detail="User not in organization")

    role = db.query(Role).filter(Role.id == org_user.role_id).first()

    if not role:
        raise HTTPException(status_code=500, detail="Role not found")

    return {
        "user_id": str(user.id),
        "organization_id": str(organization_id),
        "email": user.email,
        "role": role.name,
        "role_id": str(role.id)
    }


# =========================
# ADMIN GUARD
# =========================
def require_admin(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only"
        )
    return current_user

# =========================
# DEFAULT ORG ADMIN (SUPER ADMIN)
# =========================
DEFAULT_ORG_ID = "23158484-0000-0000-0000-000000000001"  # ajusta si usas otro

def require_default_admin(current_user=Depends(get_current_user)):
    if current_user["organization_id"] != DEFAULT_ORG_ID:
        raise HTTPException(
            status_code=403,
            detail="Not default organization"
        )

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin required"
        )

    return current_user