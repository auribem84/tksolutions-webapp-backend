from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import uuid4

from app.api.deps import get_db, get_current_user, require_default_admin
from app.models.invoice import Invoice
from app.models.invoice_details import InvoiceDetail
from app.services.invoice_pdf import generate_invoice_pdf, serialize_invoice

router = APIRouter()


def _save_line_items(db: Session, invoice_id, line_items: list) -> float:
    """Delete existing line items and insert new ones. Returns computed total."""
    db.query(InvoiceDetail).filter(InvoiceDetail.invoice_id == invoice_id).delete()
    total = 0.0
    for item in line_items:
        qty = float(item.get("quantity", 1)) or 1
        price = float(item.get("unit_price", 0))
        item_total = qty * price
        total += item_total
        db.add(InvoiceDetail(
            id=uuid4(),
            invoice_id=invoice_id,
            title=item.get("title", ""),
            description=item.get("description", ""),
            quantity=int(qty),
            unit_price=price,
        ))
    return total


@router.post("/")
def create_invoice(
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(require_default_admin),
):
    line_items = data.get("line_items") or []
    amount = sum(
        float(i.get("quantity", 1)) * float(i.get("unit_price", 0))
        for i in line_items
    ) if line_items else float(data.get("amount", 0))

    invoice = Invoice(
        id=uuid4(),
        organization_id=data["organization_id"],
        amount=amount,
        description=data.get("description"),
        status=data.get("status", "pending"),
        due_date=data.get("due_date") or None,
    )
    db.add(invoice)
    db.flush()

    if line_items:
        _save_line_items(db, invoice.id, line_items)

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

    if "description" in data:
        invoice.description = data["description"]
    if "status" in data:
        invoice.status = data["status"]
    if "due_date" in data:
        invoice.due_date = data["due_date"] or None

    if "line_items" in data:
        total = _save_line_items(db, invoice.id, data["line_items"])
        invoice.amount = total
    elif "amount" in data:
        invoice.amount = data["amount"]

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
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice_data = serialize_invoice(invoice, db)
    pdf = generate_invoice_pdf(invoice_data)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="INV-{invoice_data["short_id"]}.pdf"'},
    )
