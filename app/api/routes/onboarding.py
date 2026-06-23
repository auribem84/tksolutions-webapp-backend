from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db
from app.models.onboarding import OnboardingInvite, OnboardingSubmission

router = APIRouter()


@router.get("/{token}")
def get_onboarding(token: str, db: Session = Depends(get_db)):
    invite = db.query(OnboardingInvite).filter(OnboardingInvite.token == token).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid or expired link")
    if invite.status == "completed":
        raise HTTPException(status_code=410, detail="This form has already been submitted")
    if invite.expires_at < datetime.utcnow():
        invite.status = "expired"
        db.commit()
        raise HTTPException(status_code=410, detail="This invitation link has expired")
    return {"email": invite.email}


@router.post("/{token}", status_code=201)
def submit_onboarding(token: str, data: dict, db: Session = Depends(get_db)):
    invite = db.query(OnboardingInvite).filter(OnboardingInvite.token == token).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid or expired link")
    if invite.status == "completed":
        raise HTTPException(status_code=410, detail="This form has already been submitted")
    if invite.expires_at < datetime.utcnow():
        invite.status = "expired"
        db.commit()
        raise HTTPException(status_code=410, detail="This invitation link has expired")

    if not data.get("company_legal_name", "").strip():
        raise HTTPException(status_code=422, detail="Company legal name is required")

    submission = OnboardingSubmission(
        invite_id=invite.id,
        company_legal_name=data.get("company_legal_name", "").strip(),
        company_address_street=data.get("company_address_street"),
        company_address_city=data.get("company_address_city"),
        company_address_state=data.get("company_address_state"),
        company_address_zip=data.get("company_address_zip"),
        company_address_country=data.get("company_address_country"),
        entity_type=data.get("entity_type"),
        state_of_incorporation=data.get("state_of_incorporation"),
        signing_authority_name=data.get("signing_authority_name"),
        signing_authority_title=data.get("signing_authority_title"),
        primary_contact_name=data.get("primary_contact_name"),
        primary_contact_title=data.get("primary_contact_title"),
        primary_contact_email=data.get("primary_contact_email"),
        primary_contact_phone=data.get("primary_contact_phone"),
        billing_contact_name=data.get("billing_contact_name"),
        billing_contact_email=data.get("billing_contact_email"),
    )
    db.add(submission)
    invite.status = "completed"
    db.commit()

    return {"message": "Form submitted successfully. Thank you!"}
