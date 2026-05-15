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
# GET INVOICES (FRONTEND CONSUMES THIS)
# =========================================

@router.get("")
def get_invoices(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not hasattr(current_user, "organization_id"):
        raise HTTPException(status_code=400, detail="Missing organization_id")

    invoices = db.query(Invoice).filter(
        Invoice.organization_id == current_user.organization_id
    ).all()

    return invoices


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