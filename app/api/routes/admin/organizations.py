# app/api/routes/admin/organizations.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, require_default_admin
from app.models.organization import Organization

from app.schemas.organization import (
    OrganizationCreateFull,
    OrganizationBootstrapCreate,
    OrganizationOut,
)

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

    return {
        "organization_id": org.id,
        "user_id": user.id,
        "message": "Organization bootstrap successful"
    }


@router.get("/{org_id}")
def get_organization(org_id: UUID, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "Not found")
    return org


@router.put("/{org_id}")
def update_organization(org_id: UUID, data: dict, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org:
        raise HTTPException(404, "Not found")

    org.name = data.get("name", org.name)
    db.commit()
    return {"message": "updated"}


@router.delete("/{org_id}")
def deactivate_organization(org_id: UUID, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    org = db.query(Organization).filter(Organization.id == org_id).first()

    if not org:
        raise HTTPException(404, "Not found")

    org.is_active = False
    db.commit()
    return {"message": "deactivated"}