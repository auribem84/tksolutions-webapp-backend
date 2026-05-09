from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

from app.api.deps import get_db
from app.models.organization import Organization
from app.models.invitation import Invitation
from app.models.user import User
from app.services.email_service import send_invitation_email

router = APIRouter()


@router.post("/bootstrap")
def bootstrap_organization(data: dict, db: Session = Depends(get_db)):
    # 1. Create organization
    org = Organization(
        name=data["org_name"],
        contact_email=data.get("org_contact_email"),
        contact_phone=data.get("org_contact_phone"),
        address=data.get("org_address"),
    )
    db.add(org)
    db.flush()  # get org.id

    # 2. Create invitation instead of user
    token = str(uuid4())

    invitation = Invitation(
        email=data["admin_email"],
        role=data.get("admin_role", "admin"),
        organization_id=org.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )

    db.add(invitation)
    db.commit()

    # 3. Send email
    invite_link = f"https://my.teknowsolutions.com/accept-invite?token={token}"

    send_invitation_email(
        data["admin_email"],
        invite_link,
    )

    return {
        "message": "Organization created and invitation sent",
        "organization_id": str(org.id),
    }