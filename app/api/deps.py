from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM
from app.core.constants import DEFAULT_ORG_ID

security = HTTPBearer()


# ✅ DB Dependency (define here, don't import it)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Current User Dependency
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        organization_id = payload.get("organization_id")
        role_id = payload.get("role_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Attach dynamic attributes
    user.organization_id = organization_id
    user.role_id = role_id

    return user

def require_default_admin(current_user=Depends(get_current_user)):
    if str(current_user.organization_id) != str(DEFAULT_ORG_ID):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed: requires default org admin"
        )
    return current_user