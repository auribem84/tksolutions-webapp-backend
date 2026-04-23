# app/api/routes/admin/invitations.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import uuid4

from app.api.deps import get_db, require_default_admin
from app.services.email_service import send_email

router = APIRouter()

@router.post("/send")
def send_invitation(data: dict, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    token = str(uuid4())

    invite_link = f"http://localhost:8080/onboarding?token={token}"

    send_email(
        to=data["email"],
        subject="You're invited",
        body=f"Click here: {invite_link}"
    )

    return {"message": "Invitation sent"}