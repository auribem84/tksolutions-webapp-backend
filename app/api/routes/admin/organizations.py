# app/api/routes/admin/organizations.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, require_default_admin
from app.models.organization import Organization
from app.models.organization_profile import OrganizationProfile
from app.models.organization_contact import OrganizationContact
from app.models.user import User
from app.models.role import Role
from app.models.organization_user import OrganizationUser
from app.core.security import hash_password

from app.schemas.organization import (
    OrganizationCreateFull,
    OrganizationBootstrapCreate,
    OrganizationOut,
)
from app.services.email_service import send_welcome_email

import uuid

router = APIRouter()


@router.get("/")
def list_organizations(db: Session = Depends(get_db), user=Depends(require_default_admin)):
    return db.query(Organization).all()


# =========================================
# CREATE ORGANIZATION ONLY
# =========================================

@router.post("/create")
def create_organization(
    data: OrganizationBootstrapCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_default_admin),
):

    # =========================================
    # CREATE ORGANIZATION
    # =========================================

    org = Organization(
        id=uuid.uuid4(),
        name=data.org_name,
    )

    db.add(org)
    db.flush()

    # =========================================
    # CREATE ORGANIZATION PROFILE
    # =========================================

    profile = OrganizationProfile(
        id=uuid.uuid4(),

        organization_id=org.id,

        itin=data.itin,

        address1=data.address1,
        address2=data.address2,

        city=data.city,
        state=data.state,
        zip=data.zip,

        phone=data.phone,
        email=data.email,
    )

    db.add(profile)

    # =========================================
    # CREATE CONTACTS
    # =========================================

    for contact in data.contacts:

        new_contact = OrganizationContact(
            id=uuid.uuid4(),

            organization_id=org.id,

            contact_name=contact.contact_name,
            contact_lastname=contact.contact_lastname,
            contact_title=contact.contact_title,

            contact_email=contact.contact_email,
            contact_phone=contact.contact_phone,
            contact_mobile=contact.contact_mobile,
        )

        db.add(new_contact)

    # =========================================
    # SAVE
    # =========================================

    db.commit()

    return {
        "organization_id": org.id,
        "message": "Organization created successfully"
    }



# =========================
# BOOTSTRAP ORGANIZATION + FIRST ADMIN
# =========================
@router.post("/bootstrap")
def create_organization_with_admin(
    data: OrganizationBootstrapCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_default_admin),
):

    # =========================================
    # CREATE ORGANIZATION
    # =========================================

    org = Organization(
        id=uuid.uuid4(),
        name=data.org_name,
    )

    db.add(org)
    db.flush()

    # =========================================
    # CREATE ORGANIZATION PROFILE
    # =========================================

    profile = OrganizationProfile(
        id=uuid.uuid4(),
        organization_id=org.id,

        itin=data.itin,

        address1=data.address1,
        address2=data.address2,

        city=data.city,
        state=data.state,
        zip=data.zip,

        phone=data.phone,
        email=data.email,
    )

    db.add(profile)

    # =========================================
    # CREATE CONTACTS
    # =========================================

    for contact in data.contacts:

        new_contact = OrganizationContact(
            id=uuid.uuid4(),

            organization_id=org.id,

            contact_name=contact.contact_name,
            contact_lastname=contact.contact_lastname,
            contact_title=contact.contact_title,

            contact_email=contact.contact_email,
            contact_phone=contact.contact_phone,
            contact_mobile=contact.contact_mobile,
        )

        db.add(new_contact)

    # =========================================
    # CREATE ADMIN USER
    # =========================================

    user = User(
        id=uuid.uuid4(),

        email=data.admin_email,

        hashed_password=hash_password(
            data.admin_password
        ),

        is_active=True,
    )

    db.add(user)
    db.flush()

    # =========================================
    # ENSURE ADMIN ROLE
    # =========================================

    admin_role = db.query(Role).filter(
        Role.name == "admin"
    ).first()

    if not admin_role:

        admin_role = Role(
            id=uuid.uuid4(),
            name="admin"
        )

        db.add(admin_role)
        db.flush()

    # =========================================
    # LINK USER TO ORG
    # =========================================

    link = OrganizationUser(
        user_id=user.id,
        organization_id=org.id,
        role_id=admin_role.id,
    )

    db.add(link)

    db.commit()

    try:
        send_welcome_email(to_email=data.admin_email, first_name=data.admin_name)
    except Exception:
        pass  # don't fail the request if email delivery fails

    return {
        "organization_id": org.id,
        "user_id": user.id,
        "message": "Organization bootstrap successful"
    }


@router.post("/full")
def create_organization_full(
    data: OrganizationCreateFull,
    db: Session = Depends(get_db),
    current_user=Depends(require_default_admin),
):
    # 1. Organization
    org = Organization(
        id=uuid.uuid4(),
        name=data.org_name,
    )
    db.add(org)
    db.flush()

    # 2. Profile
    profile = OrganizationProfile(
        organization_id=org.id,
        itin=data.itin,
        address1=data.address1,
        address2=data.address2,
        city=data.city,
        state=data.state,
        zip=data.zip,
        phone=data.phone,
        email=data.email,
    )
    db.add(profile)

    # 3. Contacts
    for idx, c in enumerate(data.contacts):
        contact = OrganizationContact(
            id=uuid.uuid4(),
            organization_id=org.id,
            contact_name=c.contact_name,
            contact_lastname=c.contact_lastname,
            contact_title=c.contact_title,
            contact_email=c.contact_email,
            contact_phone=c.contact_phone,
            contact_mobile=c.contact_mobile,
            is_primary=(idx == 0),  # 👈 primer contacto como primary
        )
        db.add(contact)

    db.commit()

    return {
        "organization_id": org.id,
        "message": "Organization created successfully with profile and contacts"
    }


@router.get("/{org_id}/full")
def get_organization_full(org_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Not found")
    profile = db.query(OrganizationProfile).filter(OrganizationProfile.organization_id == org_id).first()
    contacts = db.query(OrganizationContact).filter(OrganizationContact.organization_id == org_id).order_by(OrganizationContact.created_at).all()
    return {
        "id": str(org.id),
        "name": org.name,
        "profile": {
            "itin": profile.itin or "",
            "address1": profile.address1 or "",
            "address2": profile.address2 or "",
            "city": profile.city or "",
            "state": profile.state or "",
            "zip": profile.zip or "",
            "phone": profile.phone or "",
            "email": profile.email or "",
        } if profile else {},
        "contacts": [
            {
                "id": str(c.id),
                "contact_name": c.contact_name or "",
                "contact_lastname": c.contact_lastname or "",
                "contact_title": c.contact_title or "",
                "contact_email": c.contact_email or "",
                "contact_phone": c.contact_phone or "",
                "contact_mobile": c.contact_mobile or "",
                "is_primary": c.is_primary or False,
            }
            for c in contacts
        ],
    }


@router.post("/{org_id}/contacts")
def create_contact(org_id: str, data: dict, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    contact = OrganizationContact(
        id=uuid.uuid4(),
        organization_id=org_id,
        contact_name=data.get("contact_name", ""),
        contact_lastname=data.get("contact_lastname"),
        contact_title=data.get("contact_title"),
        contact_email=data.get("contact_email"),
        contact_phone=data.get("contact_phone"),
        contact_mobile=data.get("contact_mobile"),
        is_primary=data.get("is_primary", False),
    )
    db.add(contact)
    db.commit()
    return {"id": str(contact.id), "message": "Contact created"}


@router.patch("/{org_id}/contacts/{contact_id}")
def update_contact(org_id: str, contact_id: str, data: dict, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    contact = db.query(OrganizationContact).filter(
        OrganizationContact.id == contact_id,
        OrganizationContact.organization_id == org_id,
    ).first()
    if not contact:
        raise HTTPException(404, "Contact not found")
    for field in ("contact_name", "contact_lastname", "contact_title", "contact_email", "contact_phone", "contact_mobile", "is_primary"):
        if field in data:
            setattr(contact, field, data[field])
    db.commit()
    return {"message": "Contact updated"}


@router.delete("/{org_id}/contacts/{contact_id}")
def delete_contact(org_id: str, contact_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    contact = db.query(OrganizationContact).filter(
        OrganizationContact.id == contact_id,
        OrganizationContact.organization_id == org_id,
    ).first()
    if not contact:
        raise HTTPException(404, "Contact not found")
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted"}


@router.get("/{org_id:uuid}")
def get_organization(org_id: UUID, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Not found")
    return org


# =========================================
# UPDATE ORGANIZATION
# =========================================

@router.put("/{organization_id}")
def update_organization(
    organization_id: str,
    data: OrganizationCreateFull,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):

    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    organization.name = data.org_name

    profile = db.query(OrganizationProfile).filter(
        OrganizationProfile.organization_id == organization_id
    ).first()

    if profile:
        profile.itin = data.itin
        profile.address1 = data.address1
        profile.address2 = data.address2
        profile.city = data.city
        profile.state = data.state
        profile.zip = data.zip
        profile.phone = data.phone
        profile.email = data.email

    db.commit()

    return {
        "success": True
    }


# =========================================
# DELETE ORGANIZATION
# =========================================

@router.delete("/{organization_id}")
def delete_organization(
    organization_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):

    organization = db.query(Organization).filter(
        Organization.id == organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    # DELETE CONTACTS
    db.query(OrganizationContact).filter(
        OrganizationContact.organization_id == organization_id
    ).delete()

    # DELETE PROFILE
    db.query(OrganizationProfile).filter(
        OrganizationProfile.organization_id == organization_id
    ).delete()

    # DELETE ORGANIZATION
    db.delete(organization)

    db.commit()

    return {
        "success": True
    }