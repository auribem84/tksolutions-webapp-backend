from app.models.ticket import Ticket

def generate_ticket_ref(db):
    last_ticket = (
        db.query(Ticket)
        .order_by(Ticket.created_at.desc())
        .first()
    )

    if not last_ticket or not last_ticket.ref:
        return "TK-001"

    try:
        number = int(last_ticket.ref.replace("TK-", ""))
    except ValueError:
        number = 0

    return f"TK-{str(number + 1).zfill(3)}"