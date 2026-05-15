from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4
from decimal import Decimal
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.invoice import Invoice
from app.models.invoice_details import InvoiceDetail
from app.models.organization import Organization
from app.schemas.invoice import InvoiceCreate, InvoiceOut

router = APIRouter(tags=["invoices"])

# =========================================
# LIST INVOICES (ORG SAFE - FIXED)
# =========================================
@router.get("/")
def get_invoices(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    org_id = current_user.get("organization_id")

    if not org_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user context (missing organization_id)"
        )

    invoices = db.query(Invoice).filter(
        Invoice.organization_id == org_id
    ).order_by(Invoice.created_at.desc()).all()

    result = []

    for inv in invoices:

        items = db.query(InvoiceDetail).filter(
            InvoiceDetail.invoice_id == inv.id
        ).all()

        result.append({
            "id": str(inv.id),
            "organization_id": str(inv.organization_id),

            "subtotal": float(inv.subtotal or 0),
            "tax_amount": float(inv.tax_amount or 0),
            "discount_amount": float(inv.discount_amount or 0),
            "total": float(inv.total or 0),

            "status": inv.status,
            "created_at": inv.created_at.strftime("%b %d, %Y") if inv.created_at else None,

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
            ],
        })

    return result


# =========================================
# CREATE INVOICE
# =========================================

@router.post("", response_model=InvoiceOut)
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # validate organization
    organization = db.query(Organization).filter(
        Organization.id == data.organization_id
    ).first()

    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    invoice = Invoice(
        id=uuid4(),
        organization_id=data.organization_id,
        amount=data.amount,
        description=data.description,
        status="pending",
        due_date=data.due_date
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice