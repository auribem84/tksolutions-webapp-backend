from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

from app.api.deps import get_db
from app.models.organization import Organization
from app.models.user import User
from app.models.invitation import Invitation
from app.schemas.bootstrap import BootstrapRequest
from app.core.security import hash_password as get_password_hash
from app.services.email_service import send_invitation_email

router = APIRouter()


@router.post("/bootstrap")
def bootstrap_organization(
    data: BootstrapRequest,
    db: Session = Depends(get_db),
):

    # 🧠 1. prevent double bootstrap (SaaS safety)
    existing = db.query(Organization).first()
    if existing:
        return {
            "message": "Organization already exists",
            "organization_id": str(existing.id),
        }

    # 🏢 2. create org
    org = Organization(
        id=uuid4(),
        name=data.org_name,
        contact_email=data.org_contact_email,
        contact_phone=data.org_contact_phone,
        address=data.org_address,
    )

    db.add(org)
    db.flush()

    # 👤 3. create admin user (SAFE FALLBACK)
    admin = User(
        id=uuid4(),
        email=data.admin_email,
        full_name="Admin",
        role=data.admin_role,
        organization_id=org.id,
        hashed_password=get_password_hash("TempPass123!"),
        is_active=True,
    )

    db.add(admin)

    # ✉️ 4. optional invitation (onboarding UX)
    token = str(uuid4())

    invitation = Invitation(
        email=data.admin_email,
        role=data.admin_role,
        organization_id=org.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )

    db.add(invitation)

    db.commit()

    # 📧 5. send email (non-blocking conceptually)
    invite_link = f"https://my.teknowsolutions.com/accept-invite?token={token}"
    send_invitation_email(data.admin_email, invite_link)

    return {
        "message": "Organization bootstrapped successfully",
        "organization_id": str(org.id),
    }