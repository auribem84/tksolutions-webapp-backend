from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_default_admin
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.ticket import Ticket
from app.models.organization import Organization
from app.models.user import User
from app.models.role import Role
from app.models.service import Service
from app.models.organization_user import OrganizationUser

router = APIRouter()

@router.get("/{org_id}/users")
def users(
    org_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin)
):

    rows = (
        db.query(User, OrganizationUser, Role)
        .join(OrganizationUser, OrganizationUser.user_id == User.id)
        .outerjoin(Role, Role.id == OrganizationUser.role_id)
        .filter(OrganizationUser.organization_id == org_id)
        .all()
    )

    return [
        {
            "id": str(u.id),
            "email": u.email,
            "user_name": u.user_name,
            "user_lastname": u.user_lastname,
            "full_name": f"{u.user_name} {u.user_lastname}",
            "role": r.name if r else "user",
            "is_active": u.is_active,
        }
        for u, ou, r in rows
    ]


@router.get("/{org_id}/services")
def services(
    org_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin)
):

    services = db.query(Service).filter(
        Service.organization_id == org_id
    ).all()

    return [
        {
            "id": str(s.id),
            "name": s.name,
            "description": s.description,
            "status": s.status,
        }
        for s in services
    ]


@router.get("/{org_id}/invoices")
def invoices(org_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):

    invoices = db.query(Invoice).filter(
        Invoice.organization_id == org_id
    ).all()

    return [
        {
            "id": str(i.id),
            "amount": float(i.amount),
            "description": i.description,
            "status": i.status,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i in invoices
    ]


@router.get("/{org_id}/projects")
def projects(org_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    return db.query(Project).filter(Project.organization_id == org_id).all()


@router.get("/{org_id}/tickets")
def tickets(org_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    return db.query(Ticket).filter(Ticket.organization_id == org_id).all()