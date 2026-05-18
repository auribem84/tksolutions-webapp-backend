from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_default_admin
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.ticket import Ticket
from app.models.organization import Organization

router = APIRouter()

@router.get("/{org_id}/invoices")
def invoices(org_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    return db.query(Invoice).filter(Invoice.organization_id == org_id).all()


@router.get("/{org_id}/projects")
def projects(org_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    return db.query(Project).filter(Project.organization_id == org_id).all()


@router.get("/{org_id}/tickets")
def tickets(org_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    return db.query(Ticket).filter(Ticket.organization_id == org_id).all()