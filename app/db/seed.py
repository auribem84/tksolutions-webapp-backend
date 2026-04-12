# app/db/seed.py

import uuid
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.user import User
from app.models.role import Role
from app.models.organization_user import OrganizationUser
from app.core.security import hash_password
from app.core.constants import DEFAULT_ORG_ID, DEFAULT_ADMIN_EMAIL


def create_default_org(db: Session):

    # 1. Default organization
    org = db.query(Organization).filter(
        Organization.id == DEFAULT_ORG_ID
    ).first()

    if not org:
        org = Organization(
            id=DEFAULT_ORG_ID,
            name="TKDefaultOrg"
        )
        db.add(org)

    # 2. Roles
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin")
        db.add(admin_role)

    member_role = db.query(Role).filter(Role.name == "member").first()
    if not member_role:
        member_role = Role(name="member")
        db.add(member_role)

    db.flush()

    # 3. Default admin user
    admin_user = db.query(User).filter(User.email == DEFAULT_ADMIN_EMAIL).first()

    if not admin_user:
        admin_user = User(
            email=DEFAULT_ADMIN_EMAIL,
            hashed_password=hash_password("admin123"),  # change later
            is_active=True,
        )
        db.add(admin_user)
        db.flush()

    # 4. Link admin to org
    link = db.query(OrganizationUser).filter_by(
        user_id=admin_user.id,
        organization_id=org.id
    ).first()

    if not link:
        link = OrganizationUser(
            user_id=admin_user.id,
            organization_id=org.id,
            role_id=admin_role.id
        )
        db.add(link)

    db.commit()