from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from uuid import uuid4
from datetime import datetime, timedelta
import os

from app.api.deps import get_db, require_default_admin
from app.models.invitation import Invitation
from app.schemas.invitation import InvitationCreate, InvitationAccept
from app.services.email_service import send_invitation_email

router = APIRouter()


@router.post("/")
def send_invitation(
    data: InvitationCreate,
    db: Session = Depends(get_db),
):
    token = str(uuid4())

    invitation = Invitation(
        email=data.email,
        role=data.role,
        organization_id=data.organization_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )

    db.add(invitation)
    db.commit()

    invite_link = (
        f"https://my.teknowsolutions.com/accept-invite?token={token}"
    )

    send_invitation_email(
        data.email,
        invite_link,
    )

    return {
        "message": "Invitation sent"
    }

@router.post("/accept")
def accept_invitation(
    data: InvitationAccept,
    db: Session = Depends(get_db),
):
    invitation = db.query(Invitation).filter(
        Invitation.token == data.token
    ).first()

    if not invitation:
        raise HTTPException(404, "Invalid invitation")

    if invitation.accepted:
        raise HTTPException(400, "Already used invitation")

    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(400, "Invitation expired")

    # 🧠 crear usuario real
    user = User(
        email=invitation.email,
        full_name=data.full_name,
        role=invitation.role,
        organization_id=invitation.organization_id,
        hashed_password=hash_password(data.password),
        is_active=True,
    )

    db.add(user)

    # marcar invitation como usada
    invitation.accepted = True

    db.commit()

    return {"message": "Account created successfully"}

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