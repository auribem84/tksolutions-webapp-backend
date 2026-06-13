from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from uuid import uuid4
from datetime import datetime, timedelta
import os

from app.api.deps import get_db, require_default_admin
from app.models.invitation import Invitation
from app.models.user import User
from app.models.organization import Organization
from app.models.organization_user import OrganizationUser
from app.schemas.invitation import InvitationCreate, InvitationAccept
from app.services.email_service import send_invitation_email, send_welcome_email
from app.core.security import hash_password

router = APIRouter()


@router.get("/preview")
def preview_invitation(token: str, db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(Invitation.token == token).first()

    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid invitation link.")

    if invitation.accepted:
        raise HTTPException(status_code=400, detail="This invitation has already been used.")

    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="This invitation has expired.")

    org = db.query(Organization).filter(Organization.id == invitation.organization_id).first()

    return {
        "email": invitation.email,
        "organization": org.name if org else None,
        "role": invitation.role,
    }


@router.post("/accept")
def accept_invitation(data: InvitationAccept, db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(Invitation.token == data.token).first()

    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid invitation link.")

    if invitation.accepted:
        raise HTTPException(status_code=400, detail="This invitation has already been used.")

    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="This invitation has expired.")

    existing = db.query(User).filter(User.email == invitation.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = User(
        email=invitation.email,
        user_name=data.user_name,
        user_lastname=data.user_lastname,
        hashed_password=hash_password(data.password),
        is_active=True,
    )
    db.add(user)
    db.flush()

    org_user = OrganizationUser(
        user_id=user.id,
        organization_id=invitation.organization_id,
        role_id=os.getenv("DEFAULT_ROLE_ID"),
    )
    db.add(org_user)

    invitation.accepted = True
    db.commit()

    try:
        send_welcome_email(invitation.email, data.user_name)
    except Exception as e:
        print(f"WELCOME EMAIL ERROR: {e}")

    return {"message": "Account created successfully."}


@router.post("/send")
def send_invitation_admin(data: dict, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    email = data.get("email")
    organization_id = data.get("organization_id")
    role = data.get("role", "user")

    if not email or not organization_id:
        raise HTTPException(status_code=422, detail="email and organization_id are required")

    token = str(uuid4())

    invitation = Invitation(
        email=email,
        role=role,
        organization_id=organization_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(invitation)
    db.commit()

    frontend_url = os.getenv("FRONTEND_URL", "https://my.teknowsolutions.com")
    invite_link = f"{frontend_url}/accept-invite?token={token}"

    send_invitation_email(email, invite_link)

    return {"message": "Invitation sent"}
