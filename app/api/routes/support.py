from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.ticket import Ticket, TicketCreate
from app.models.ticket_message import TicketMessage


router = APIRouter()


# 📄 LIST SUPPORT TICKETS (ORG SAFE)
@router.get("/")
def get_tickets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    org_id = current_user.get("organization_id")

    if not org_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user context (missing organization_id)"
        )

    tickets = db.query(Ticket).filter(
        Ticket.organization_id == org_id
    ).all()

    result = []

    for t in tickets:
        messages = db.query(TicketMessage).filter(
            TicketMessage.ticket_id == t.id
        ).order_by(TicketMessage.created_at.asc()).all()

        result.append({
            "id": str(t.id),
            "ref": t.ref,
            "subject": t.subject,
            "status": t.status,
            "priority": t.priority,
            "created": t.created_at.strftime("%b %d, %Y"),
            "updated": t.updated_at.strftime("%b %d, %Y"),
            "assignee": t.assignee,
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
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ref = generate_ticket_ref(db)

    ticket = Ticket(
        ref=ref,
        subject=data.subject,
        priority=data.priority or "medium",
        organization_id=current_user["organization_id"],
        status="open",
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "id": str(ticket.id),
        "ref": ticket.ref,   # 👈 esto es lo que usa el frontend
        "subject": ticket.subject,
        "status": ticket.status,
        "priority": ticket.priority,
        "created": ticket.created_at.strftime("%b %d, %Y"),
        "updated": ticket.updated_at.strftime("%b %d, %Y"),
        "assignee": ticket.assignee,
        "messages": [],
    }