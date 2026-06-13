from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_default_admin
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.ticket import Ticket, TicketMessage
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
    rows = db.query(Project).filter(Project.organization_id == org_id).all()
    return [
        {
            "id": str(p.id),
            "project_tag": p.project_tag,
            "name": p.name,
            "description": p.description,
            "notes": p.notes,
            "status": p.status,
        }
        for p in rows
    ]


@router.get("/{org_id}/tickets")
def get_tickets(org_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    ticket_rows = db.query(Ticket).filter(Ticket.organization_id == org_id).order_by(Ticket.created_at.desc()).all()

    result = []
    for t in ticket_rows:
        messages = (
            db.query(TicketMessage)
            .filter(TicketMessage.ticket_id == t.id)
            .order_by(TicketMessage.created_at.asc())
            .all()
        )
        result.append({
            "id": t.id,
            "ref": t.ref,
            "subject": t.subject,
            "status": t.status,
            "priority": t.priority,
            "assignee": t.assignee or "Unassigned",
            "created": t.created_at.strftime("%b %d, %Y") if t.created_at else None,
            "messages": [
                {
                    "sender": m.sender,
                    "text": m.text,
                    "time": m.created_at.strftime("%b %d, %I:%M %p") if m.created_at else None,
                }
                for m in messages
            ],
        })
    return result


@router.post("/{org_id}/tickets/{ticket_id}/messages")
def reply_ticket(
    org_id: str,
    ticket_id: str,
    data: dict,
    db: Session = Depends(get_db),
    admin=Depends(require_default_admin),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == org_id,
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    text = data.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="Reply text is required")

    admin_user = db.query(User).filter(User.id == admin["user_id"]).first()
    sender = admin_user.email if admin_user else "Admin"

    message = TicketMessage(ticket_id=ticket.id, sender=sender, text=text)
    db.add(message)

    ticket.status = "in_progress"
    ticket.updated_at = __import__("datetime").datetime.utcnow()

    db.commit()
    db.refresh(message)

    return {
        "sender": message.sender,
        "text": message.text,
        "time": message.created_at.strftime("%b %d, %I:%M %p") if message.created_at else None,
    }