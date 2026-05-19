from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user

from app.models.invoice import Invoice

from app.services.invoice_pdf import (
    serialize_invoice,
    generate_invoice_pdf,
    render_invoice_email,
)

from app.services.email_service import (
    send_invoice_email
)

router = APIRouter()

@router.post("/send-invoice/{invoice_id}")
def send_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    # SERIALIZE
    invoice_data = serialize_invoice(invoice, db)

    # GENERATE PDF
    pdf_buffer = generate_invoice_pdf(invoice_data)

    # EMAIL HTML
    email_html = render_invoice_email(invoice_data)

    recipient_email = (
        invoice_data["organization_profile"]["email"]
    )

    if not recipient_email:
        raise HTTPException(
            status_code=400,
            detail="Organization email not found"
        )

    # SEND EMAIL
    send_invoice_email(
        recipient_email=recipient_email,

        subject=(
            f"Invoice INV-{invoice_data['short_id']}"
        ),

        body_html=email_html,

        pdf_bytes=pdf_buffer.getvalue(),

        filename=(
            f"INV-{invoice_data['short_id']}.pdf"
        )
    )

    return {
        "success": True,
        "message": "Invoice email sent"
    }