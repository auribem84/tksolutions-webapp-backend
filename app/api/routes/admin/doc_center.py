from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os

from app.api.deps import get_db, require_default_admin
from app.models.onboarding import OnboardingInvite, OnboardingSubmission
from app.services.email_service import send_onboarding_invite_email

router = APIRouter()

INVITE_EXPIRE_DAYS = 7


@router.post("/invite", status_code=201)
def send_invite(data: dict, db: Session = Depends(get_db), current_user=Depends(require_default_admin)):
    email = data.get("email", "").strip()
    if not email:
        raise HTTPException(status_code=422, detail="Email is required")

    invite = OnboardingInvite(
        email=email,
        expires_at=datetime.utcnow() + timedelta(days=INVITE_EXPIRE_DAYS),
        created_by=current_user.get("email"),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    form_link = f"{frontend_url}/onboarding/{invite.token}"

    try:
        send_onboarding_invite_email(email, form_link)
    except Exception as e:
        print("EMAIL ERROR:", e)

    return {"message": "Invite sent", "id": str(invite.id)}


@router.get("/invites")
def list_invites(db: Session = Depends(get_db), _=Depends(require_default_admin)):
    invites = db.query(OnboardingInvite).order_by(OnboardingInvite.created_at.desc()).all()
    result = []
    for inv in invites:
        if inv.status == "pending" and inv.expires_at < datetime.utcnow():
            inv.status = "expired"
            db.commit()
        result.append({
            "id": str(inv.id),
            "email": inv.email,
            "status": inv.status,
            "created_at": inv.created_at.isoformat() if inv.created_at else None,
            "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
            "created_by": inv.created_by,
        })
    return result


@router.get("/submissions")
def list_submissions(db: Session = Depends(get_db), _=Depends(require_default_admin)):
    submissions = (
        db.query(OnboardingSubmission)
        .order_by(OnboardingSubmission.submitted_at.desc())
        .all()
    )
    result = []
    for sub in submissions:
        invite = db.query(OnboardingInvite).filter(OnboardingInvite.id == sub.invite_id).first()
        result.append({
            "id": str(sub.id),
            "invite_email": invite.email if invite else "—",
            "company_legal_name": sub.company_legal_name,
            "primary_contact_name": sub.primary_contact_name,
            "primary_contact_email": sub.primary_contact_email,
            "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
        })
    return result


@router.get("/submissions/{submission_id}")
def get_submission(submission_id: str, db: Session = Depends(get_db), _=Depends(require_default_admin)):
    sub = db.query(OnboardingSubmission).filter(OnboardingSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    invite = db.query(OnboardingInvite).filter(OnboardingInvite.id == sub.invite_id).first()

    return {
        "id": str(sub.id),
        "invite_email": invite.email if invite else "—",
        "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
        "company_legal_name": sub.company_legal_name,
        "company_address_street": sub.company_address_street,
        "company_address_city": sub.company_address_city,
        "company_address_state": sub.company_address_state,
        "company_address_zip": sub.company_address_zip,
        "company_address_country": sub.company_address_country,
        "entity_type": sub.entity_type,
        "state_of_incorporation": sub.state_of_incorporation,
        "signing_authority_name": sub.signing_authority_name,
        "signing_authority_title": sub.signing_authority_title,
        "primary_contact_name": sub.primary_contact_name,
        "primary_contact_title": sub.primary_contact_title,
        "primary_contact_email": sub.primary_contact_email,
        "primary_contact_phone": sub.primary_contact_phone,
        "billing_contact_name": sub.billing_contact_name,
        "billing_contact_email": sub.billing_contact_email,
    }
