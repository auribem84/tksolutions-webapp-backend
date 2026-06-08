from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import uuid4

from app.api.deps import get_db, get_current_user, require_default_admin
from app.models.invoice import Invoice
from app.services.invoice_pdf import generate_invoice_pdf, serialize_invoice

router = APIRouter()


@router.post("/")
def create_invoice(
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    invoice = Invoice(
        id=uuid4(),
        organization_id=data["organization_id"],
        amount=data["amount"],
        description=data.get("description"),
        status=data.get("status", "pending"),
        due_date=data.get("due_date"),
    )
    db.add(invoice)
    db.commit()
    return {"message": "Invoice created", "invoice_id": str(invoice.id)}


@router.patch("/{invoice_id}")
def update_invoice(
    invoice_id: str,
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if "amount" in data:
        invoice.amount = data["amount"]
    if "description" in data:
        invoice.description = data["description"]
    if "status" in data:
        invoice.status = data["status"]
    if "due_date" in data:
        invoice.due_date = data["due_date"]

    db.commit()
    return {"message": "Invoice updated"}


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted"}

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