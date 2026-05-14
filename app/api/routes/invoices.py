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
        "message": "Invoice created successfully",

        "invoice": {
            "id": str(invoice.id),

            "organization_id": str(invoice.organization_id),

            "subtotal": invoice.subtotal,
            "tax_amount": invoice.tax_amount,
            "discount_amount": invoice.discount_amount,
            "total": invoice.total,

            "status": invoice.status
        }
    }