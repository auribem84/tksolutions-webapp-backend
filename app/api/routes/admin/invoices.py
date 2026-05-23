from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.invoice import Invoice
from app.services.invoice_pdf import generate_invoice_pdf, serialize_invoice

router = APIRouter()

@router.get("/download/{invoice_id}")
def admin_download_invoice(
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

    invoice_data = serialize_invoice(invoice, db)

    pdf = generate_invoice_pdf(invoice_data)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="INV-{invoice_data["short_id"]}.pdf"'
        }
    )