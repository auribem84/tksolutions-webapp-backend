from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketOut

router = APIRouter()


# 🔐 Admin check
def require_admin(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user


@router.get("/health")
def health():
    return {"status": "tickets router working"}


# 🎫 CREATE TICKET
@router.post("/", response_model=TicketOut)
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ticket = Ticket(
        title=data.title,
        description=data.description,
        status="open",
        organization_id=current_user["organization_id"],
        created_by=current_user["user_id"],
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


# 📄 LIST TICKETS
@router.get("/", response_model=list[TicketOut])
def list_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Ticket).filter(
        Ticket.organization_id == current_user["organization_id"]
    ).all()


# 🔍 GET ONE
@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user["organization_id"]
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


# ✏️ UPDATE
@router.put("/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: UUID,
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user["organization_id"]
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if str(ticket.created_by) != str(current_user["user_id"]) and str(current_user["role_id"]) != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")

    ticket.title = data.title
    ticket.description = data.description

    db.commit()
    db.refresh(ticket)

    return ticket


# 🔄 STATUS (ADMIN)
@router.patch("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: UUID,
    status_value: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user["organization_id"]
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = status_value
    db.commit()

    return {"message": "Status updated"}


# ❌ DELETE (ADMIN)
@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user["organization_id"]
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()

    return {"message": "Ticket deleted"}