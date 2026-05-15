from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user

from app.models.invoice import Invoice
from app.models.invoice_details import InvoiceDetail
from app.models.organization import Organization

router = APIRouter()


# =========================================
# SCHEMAS
# =========================================

class InvoiceItemCreate(BaseModel):
    title: str
    description: Optional[str] = None

    quantity: int = 1
    unit_price: float


class InvoiceCreate(BaseModel):
    organization_id: str

    items: List[InvoiceItemCreate]

    # optional
    tax_percent: float = 0
    discount_percent: float = 0


# =========================================
# CREATE INVOICE
# =========================================

@router.post("/create")
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # =========================================
    # VALIDATE ORG
    # =========================================

    organization = db.query(Organization).filter(
        Organization.id == data.organization_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    # =========================================
    # CALCULATE SUBTOTAL
    # =========================================

    subtotal = Decimal("0.00")

    for item in data.items:

        line_total = (
            Decimal(str(item.quantity))
            * Decimal(str(item.unit_price))
        )

        subtotal += line_total

    # =========================================
    # TAXES
    # =========================================

    tax_amount = (
        subtotal
        * Decimal(str(data.tax_percent))
        / Decimal("100")
    )

    # =========================================
    # DISCOUNTS
    # =========================================

    discount_amount = (
        subtotal
        * Decimal(str(data.discount_percent))
        / Decimal("100")
    )

    # =========================================
    # FINAL TOTAL
    # =========================================

    total = subtotal + tax_amount - discount_amount

    # =========================================
    # CREATE INVOICE
    # =========================================

    invoice = Invoice(
        id=uuid4(),

        organization_id=data.organization_id,

        subtotal=float(round(subtotal, 2)),
        tax_amount=float(round(tax_amount, 2)),
        discount_amount=float(round(discount_amount, 2)),
        total=float(round(total, 2)),

        status="draft"
    )

    db.add(invoice)
    db.flush()

    # =========================================
    # CREATE INVOICE ITEMS
    # =========================================

    for item in data.items:

        detail = InvoiceDetail(
            id=uuid4(),

            invoice_id=invoice.id,

            title=item.title,
            description=item.description,

            quantity=item.quantity,
            unit_price=item.unit_price,

            subtotal=float(
                round(
                    item.quantity * item.unit_price,
                    2
                )
            )
        )

        db.add(detail)

    db.commit()
    db.refresh(invoice)

    # =========================================
    # RESPONSE
    # =========================================

    return {
        "id": str(invoice.id),
        "organization_id": str(invoice.organization_id),
        "subtotal": invoice.subtotal,
        "tax_amount": invoice.tax_amount,
        "discount_amount": invoice.discount_amount,
        "total": invoice.total,
        "status": invoice.status,
        "items": [...]
    }


@router.get("")
def get_invoices(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    invoices = (
        db.query(Invoice)
        .filter(Invoice.organization_id == current_user.organization_id)
        .order_by(Invoice.id.desc())
        .all()
    )

    result = []

    for inv in invoices:

        items = (
            db.query(InvoiceDetail)
            .filter(InvoiceDetail.invoice_id == inv.id)
            .all()
        )

        result.append({
            "id": str(inv.id),
            "organization_id": str(inv.organization_id),

            "subtotal": float(inv.subtotal or 0),
            "tax_amount": float(inv.tax_amount or 0),
            "discount_amount": float(inv.discount_amount or 0),
            "total": float(inv.total or 0),

            "status": inv.status,
            "created_at": inv.created_at if hasattr(inv, "created_at") else None,

            "items": [
                {
                    "id": str(i.id),
                    "title": i.title,
                    "description": i.description,
                    "quantity": i.quantity,
                    "unit_price": float(i.unit_price),
                    "subtotal": float(i.subtotal),
                }
                for i in items
            ]
        })

    return result