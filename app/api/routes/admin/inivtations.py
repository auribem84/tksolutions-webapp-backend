from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from uuid import uuid4
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.invitation import Invitation
from app.schemas.invitation import InvitationCreate
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