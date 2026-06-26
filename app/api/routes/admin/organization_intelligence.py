from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import uuid

from app.api.deps import get_db, require_default_admin
from app.models.invoice import Invoice
from app.models.recurring_invoice import RecurringInvoice
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
    from app.models.invoice_details import InvoiceDetail

    rows = db.query(Invoice).filter(
        Invoice.organization_id == org_id
    ).order_by(Invoice.created_at.desc()).all()

    result = []
    for i in rows:
        details = (
            db.query(InvoiceDetail)
            .filter(InvoiceDetail.invoice_id == str(i.id))
            .order_by(InvoiceDetail.id)
            .all()
        )
        result.append({
            "id": str(i.id),
            "amount": float(i.amount),
            "description": i.description,
            "status": i.status,
            "due_date": i.due_date.isoformat() if i.due_date else None,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "line_items": [
                {
                    "title": d.title,
                    "description": d.description or "",
                    "quantity": d.quantity,
                    "unit_price": float(d.unit_price),
                    "total": float(d.total),
                }
                for d in details
            ],
        })
    return result


def _next_billing(day: int, from_date: datetime) -> datetime:
    """Return the next occurrence of day-of-month on or after from_date."""
    candidate = from_date.replace(day=min(day, 28))
    if candidate < from_date:
        candidate = (from_date + relativedelta(months=1)).replace(day=min(day, 28))
    return candidate


def _advance(dt: datetime, frequency: str) -> datetime:
    if frequency == "quarterly":
        return dt + relativedelta(months=3)
    if frequency == "annually":
        return dt + relativedelta(years=1)
    return dt + relativedelta(months=1)


def _serialize_recurring(r: RecurringInvoice) -> dict:
    return {
        "id": str(r.id),
        "organization_id": str(r.organization_id),
        "description": r.description,
        "amount": float(r.amount),
        "frequency": r.frequency,
        "day_of_month": r.day_of_month,
        "start_date": r.start_date.isoformat() if r.start_date else None,
        "next_billing_date": r.next_billing_date.isoformat() if r.next_billing_date else None,
        "is_active": r.is_active,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@router.get("/{org_id}/recurring-invoices")
def get_recurring_invoices(org_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    rows = db.query(RecurringInvoice).filter(
        RecurringInvoice.organization_id == org_id
    ).order_by(RecurringInvoice.created_at.desc()).all()
    return [_serialize_recurring(r) for r in rows]


@router.post("/{org_id}/recurring-invoices")
def create_recurring_invoice(org_id: str, data: dict, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    frequency = data.get("frequency", "monthly")
    day = int(data.get("day_of_month", 1))
    start_raw = data.get("start_date")
    start_dt = datetime.fromisoformat(start_raw) if start_raw else datetime.utcnow()

    if frequency == "monthly":
        next_bill = _next_billing(day, start_dt)
    else:
        next_bill = start_dt

    rec = RecurringInvoice(
        id=uuid.uuid4(),
        organization_id=org_id,
        description=data.get("description"),
        amount=float(data["amount"]),
        frequency=frequency,
        day_of_month=day,
        start_date=start_dt,
        next_billing_date=next_bill,
        is_active=data.get("is_active", True),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return _serialize_recurring(rec)


@router.patch("/{org_id}/recurring-invoices/{rec_id}")
def update_recurring_invoice(org_id: str, rec_id: str, data: dict, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    rec = db.query(RecurringInvoice).filter(
        RecurringInvoice.id == rec_id,
        RecurringInvoice.organization_id == org_id,
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recurring invoice not found")

    for field in ("description", "amount", "frequency", "day_of_month", "is_active", "next_billing_date"):
        if field in data:
            setattr(rec, field, data[field])

    db.commit()
    db.refresh(rec)
    return _serialize_recurring(rec)


@router.delete("/{org_id}/recurring-invoices/{rec_id}", status_code=204)
def delete_recurring_invoice(org_id: str, rec_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    rec = db.query(RecurringInvoice).filter(
        RecurringInvoice.id == rec_id,
        RecurringInvoice.organization_id == org_id,
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recurring invoice not found")
    db.delete(rec)
    db.commit()


@router.post("/{org_id}/recurring-invoices/{rec_id}/generate")
def generate_now(org_id: str, rec_id: str, db: Session = Depends(get_db), user=Depends(require_default_admin)):
    """Manually trigger one billing cycle: creates a regular invoice and advances next_billing_date."""
    rec = db.query(RecurringInvoice).filter(
        RecurringInvoice.id == rec_id,
        RecurringInvoice.organization_id == org_id,
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recurring invoice not found")

    from datetime import timedelta
    invoice = Invoice(
        id=uuid.uuid4(),
        organization_id=org_id,
        amount=rec.amount,
        description=rec.description,
        status="pending",
        due_date=datetime.utcnow() + timedelta(days=15),
    )
    db.add(invoice)

    base = rec.next_billing_date or datetime.utcnow()
    rec.next_billing_date = _advance(base, rec.frequency)

    db.commit()
    return {"invoice_id": str(invoice.id), "next_billing_date": rec.next_billing_date.isoformat()}


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