from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_user import OrganizationUser
from app.api.deps import get_db
from app.core.security import hash_password
from app.api.deps import get_db, get_current_user
from app.models.role import Role

router = APIRouter()


# CREATE USER
@router.post("/", response_model=UserOut)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 🔥 GET DEFAULT ORG (always same one)
    org = db.query(Organization).filter(
        Organization.name == "Default Organization"
    ).first()

    default_role = db.query(Role).filter(
        Role.name == "admin"
    ).first()

    if not default_role:
        raise HTTPException(status_code=500, detail="Default role missing")

    if not org:
        raise HTTPException(status_code=500, detail="Default org missing")

    # 🔗 LINK USER TO ORG
    org_user = OrganizationUser(
        user_id=new_user.id,
        organization_id=org.id,
        role_id=default_role.id
    )

    db.add(org_user)
    db.commit()

    return new_user


# GET ALL USERS
@router.get("/", response_model=list[UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return (
        db.query(User)
        .join(OrganizationUser, OrganizationUser.user_id == User.id)
        .filter(
            OrganizationUser.organization_id == current_user.organization_id
        )
        .all()
    )


# GET USER BY ID
@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = (
        db.query(User)
        .join(OrganizationUser, OrganizationUser.user_id == User.id)
        .filter(
            User.id == user_id,
            OrganizationUser.organization_id == current_user.organization_id
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# UPDATE USER
@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = (
        db.query(User)
        .join(OrganizationUser, OrganizationUser.user_id == User.id)
        .filter(
            User.id == user_id,
            OrganizationUser.organization_id == current_user.organization_id
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.email:
        user.email = data.email

    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)

    return user


# DELETE (SOFT DELETE)
@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = (
        db.query(User)
        .join(OrganizationUser)
        .filter(
            User.id == user_id,
            OrganizationUser.organization_id == current_user.organization_id
        )
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return {"message": "User deactivated"}