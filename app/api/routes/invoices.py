from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from uuid import uuid4
from decimal import Decimal

from datetime import datetime

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.api.deps import get_db, get_current_user
from app.models.invoice import Invoice
from app.models.invoice_details import InvoiceDetail
from app.models.organization import Organization
from app.schemas.invoice import InvoiceCreate, InvoiceOut
from app.services.invoice_pdf import generate_invoice_pdf, serialize_invoice

router = APIRouter()

# =========================================
# LIST INVOICES (ORG SAFE - FIXED)
# =========================================
@router.get("/", response_model=List[InvoiceOut])
def get_invoices(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    org_id = current_user.get("organization_id")

    if not org_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user context"
        )

    invoices = db.query(Invoice).filter(
        Invoice.organization_id == org_id
    ).order_by(Invoice.created_at.desc()).all()

    return [
        {
            "id": str(i.id),
            "organization_id": str(i.organization_id),
            "amount": float(i.amount),
            "description": i.description,
            "status": i.status,
            "due_date": str(i.due_date) if i.due_date else None,
            "created_at": i.created_at.isoformat() if i.created_at else None,
        }
        for i in invoices
    ]



# =========================================
# INVOICE STATS
# =========================================

@router.get("/stats")
def get_invoice_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    org_id = current_user.get("organization_id")

    if not org_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user context"
        )

    now = datetime.utcnow()

    current_month_invoices = db.query(
        func.coalesce(func.sum(Invoice.amount), 0)
    ).filter(
        Invoice.organization_id == org_id,
        func.extract("month", Invoice.created_at) == now.month,
        func.extract("year", Invoice.created_at) == now.year,
    ).scalar()

    outstanding = db.query(
        func.coalesce(func.sum(Invoice.amount), 0)
    ).filter(
        Invoice.organization_id == org_id,
        Invoice.status == "pending"
    ).scalar()

    paid = db.query(
        func.coalesce(func.sum(Invoice.amount), 0)
    ).filter(
        Invoice.organization_id == org_id,
        Invoice.status == "paid"
    ).scalar()

    total_invoices = db.query(Invoice).filter(
        Invoice.organization_id == org_id
    ).count()

    return {
        "current_month": float(current_month_invoices or 0),
        "outstanding": float(outstanding or 0),
        "paid": float(paid or 0),
        "total_invoices": total_invoices,
    }


# =========================================
# DOWNLOAD INVOICE PDF
# =========================================
@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    org_id = current_user.get("organization_id")

    if not org_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user context"
        )

    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.organization_id == org_id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )

    invoice_data = serialize_invoice(invoice)

    pdf = generate_invoice_pdf(invoice_data, db)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename=invoice-{invoice_data['short_id']}.pdf"
        }
    )






# =========================================
# CREATE INVOICE
# =========================================

@router.post("/", response_model=InvoiceOut)
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    org_id = current_user.get("organization_id")

    if not org_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user context"
        )

    organization = db.query(Organization).filter(
        Organization.id == org_id
    ).first()

    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    invoice = Invoice(
        id=uuid4(),
        organization_id=org_id,
        amount=data.amount,
        description=data.description,
        status="pending",
        due_date=data.due_date
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return {
        "id": str(invoice.id),
        "organization_id": str(invoice.organization_id),
        "amount": float(invoice.amount),
        "description": invoice.description,
        "status": invoice.status,
        "due_date": str(invoice.due_date) if invoice.due_date else None,
        "created_at": invoice.created_at.isoformat() if invoice.created_at else None,
    }
