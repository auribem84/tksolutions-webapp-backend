from sqlalchemy import text

def generate_ticket_ref(db):
    result = db.execute(
        text("SELECT COUNT(*) FROM tickets")
    ).scalar()

    return f"TK-{result + 1:04d}"