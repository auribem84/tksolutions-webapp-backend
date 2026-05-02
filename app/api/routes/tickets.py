from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.ticket import Ticket, TicketMessage
from app.services.ticket_ref import generate_ticket_ref

router = APIRouter()


@router.get("/")
def get_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    tickets = db.query(Ticket).filter(
        Ticket.organization_id == current_user["organization_id"]
    ).all()

    result = []

    for t in tickets:
        messages = db.query(TicketMessage).filter(
            TicketMessage.ticket_id == t.id
        ).order_by(TicketMessage.created_at.asc()).all()

        result.append({
            "id": t.id,                 # interno
            "ref": t.ref,              # público TK-001
            "subject": t.subject,
            "status": t.status,
            "priority": t.priority,
            "created": t.created_at.strftime("%b %d, %Y"),
            "updated": t.updated_at.strftime("%b %d, %Y"),
            "assignee": t.assignee or "Unassigned",
            "messages": [
                {
                    "sender": m.sender,
                    "time": m.created_at.strftime("%b %d, %I:%M %p"),
                    "text": m.text,
                }
                for m in messages
            ],
        })

    return result

@router.post("/")
def create_ticket(
    data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ref = generate_ticket_ref(db)

    # 1. crear ticket SIN description
    ticket = Ticket(
        ref=ref,
        subject=data["subject"],
        priority=data.get("priority", "medium"),
        organization_id=current_user["organization_id"],
        # created_by=current_user["email"],
        status="open",
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # 2. crear primer mensaje = description
    first_message = TicketMessage(
        ticket_id=ticket.id,
        sender=current_user["email"],
        text=data.get("description", ""),
    )

    db.add(first_message)
    db.commit()
    db.refresh(first_message)

    return {
        "id": ticket.id,
        "ref": ticket.ref,
        "subject": ticket.subject,
        "status": ticket.status,
        "priority": ticket.priority,
        "created": ticket.created_at.strftime("%b %d, %Y"),
        "updated": ticket.updated_at.strftime("%b %d, %Y"),
        # "created_by": ticket.created_by,
        "messages": [
            {
                "sender": first_message.sender,
                "time": first_message.created_at.strftime("%H:%M"),
                "text": first_message.text,
            }
        ],
    }


@router.post("/{ticket_id}/messages")
def add_message(
    ticket_id: str,
    data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    message = TicketMessage(
        ticket_id=ticket.id,
        sender=current_user["email"],  # o name
        text=data["text"],
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "sender": message.sender,
        "text": message.text,
        "time": message.created_at.strftime("%b %d, %H:%M"),
    }