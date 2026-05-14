from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user, require_admin
from app.models.billing import Billing
from app.schemas.billing import BillingCreate, BillingOut

from io import BytesIO

from fastapi.responses import Response, StreamingResponse
from jinja2 import Template
from weasyprint import HTML
from datetime import datetime

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "billings router working"}


# ➕ CREATE (ADMIN ONLY)
@router.post("/", response_model=BillingOut)
def create_billing(
    data: BillingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    billing = Billing(
        description=data.description,
        amount=data.amount,
        status="pending",
        organization_id=current_user["organization_id"],
    )

    db.add(billing)
    db.commit()
    db.refresh(billing)

    return billing


# 📄 LIST (ORG SCOPE)
@router.get("/", response_model=list[BillingOut])
def list_billings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Billing).filter(
        Billing.organization_id == current_user["organization_id"]
    ).all()


# 🔍 GET ONE
@router.get("/{billing_id}", response_model=BillingOut)
def get_billing(
    billing_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    billing = db.query(Billing).filter(
        Billing.id == billing_id,
        Billing.organization_id == current_user["organization_id"]
    ).first()

    if not billing:
        raise HTTPException(status_code=404, detail="Billing not found")

    return billing


# 🔄 UPDATE STATUS (ADMIN)
@router.patch("/{billing_id}/status")
def update_billing_status(
    billing_id: UUID,
    status_value: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    billing = db.query(Billing).filter(
        Billing.id == billing_id,
        Billing.organization_id == current_user["organization_id"]
    ).first()

    if not billing:
        raise HTTPException(status_code=404, detail="Billing not found")

    billing.status = status_value
    db.commit()

    return {"message": "Status updated"}

@router.get("/{billing_id}/pdf")
def download_invoice_pdf(
    billing_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    billing = db.query(Billing).filter(
        Billing.id == billing_id,
        Billing.organization_id == current_user["organization_id"]
    ).first()

    if not billing:
        raise HTTPException(status_code=404, detail="Billing not found")

    # 🧠 MOCK DATA (luego lo conectamos a DB real)
    data = {
        "invoice_id": str(billing.id)[:8],
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "due_date": "2026-05-01",
        "customer_name": current_user["email"],
        "customer_email": current_user["email"],
        "payment_method": "Credit Card (Visa **** 4242)",
        "status": billing.status,
        "logo_url": "https://yourcdn.com/logo.png",
        "items": [
            {
                "description": billing.description,
                "quantity": 1,
                "price": billing.amount,
                "total": billing.amount,
            }
        ],
        "total": billing.amount,
    }

    # 📄 cargar template
    with open("app/templates/invoice.html") as f:
        template = Template(f.read())

    html_content = template.render(**data)

    pdf = HTML(string=html_content).write_pdf()

    return StreamingResponse(
        iter([pdf]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice-{billing.id}.pdf"
        },
    )