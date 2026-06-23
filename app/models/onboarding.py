import uuid
import secrets
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class OnboardingInvite(Base):
    __tablename__ = "onboarding_invites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String, unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    email = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending | completed | expired
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)


class OnboardingSubmission(Base):
    __tablename__ = "onboarding_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invite_id = Column(UUID(as_uuid=True), ForeignKey("onboarding_invites.id"), nullable=False)

    # Company info
    company_legal_name = Column(String, nullable=False)
    company_address_street = Column(String)
    company_address_city = Column(String)
    company_address_state = Column(String)
    company_address_zip = Column(String)
    company_address_country = Column(String)
    entity_type = Column(String)
    state_of_incorporation = Column(String)

    # Signing authority
    signing_authority_name = Column(String)
    signing_authority_title = Column(String)

    # Primary contact
    primary_contact_name = Column(String)
    primary_contact_title = Column(String)
    primary_contact_email = Column(String)
    primary_contact_phone = Column(String)

    # Billing contact
    billing_contact_name = Column(String)
    billing_contact_email = Column(String)

    submitted_at = Column(DateTime, default=datetime.utcnow)
