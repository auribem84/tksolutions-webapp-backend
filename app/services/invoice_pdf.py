from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.models.organization_profile import OrganizationProfile

import os

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

templates = Environment(
    loader=FileSystemLoader(
        os.path.join(BASE_DIR, "templates")
    )
)


def serialize_invoice(invoice, db):

    org = invoice.organization

    profile = db.query(OrganizationProfile).filter(
        OrganizationProfile.organization_id == org.id
    ).first()

    return {

        "id": str(invoice.id),
        "short_id": str(invoice.id)[:8],

        "organization": {
            "name": org.name,
        },

        "organization_profile": {

            "address1":
                profile.address1 if profile else "",

            "address2":
                profile.address2 if profile else "",

            "city":
                profile.city if profile else "",

            "state":
                profile.state if profile else "",

            "zip":
                profile.zip if profile else "",

            "phone":
                profile.phone if profile else "",

            "email":
                profile.email if profile else "",
        },

        "invoice": {
            "amount": float(invoice.amount),
            "description": invoice.description,
            "status": invoice.status,
        }
    }






# def serialize_invoice(invoice):
#     return {
#         "id": str(invoice.id),
#         "short_id": str(invoice.id).replace("-", "")[-6:].upper(),

#         "amount": float(invoice.amount or 0),
#         "description": invoice.description or "",
#         "status": invoice.status,

#         "due_date": invoice.due_date.strftime("%B %d, %Y") if invoice.due_date else "N/A",
#         "created_at": invoice.created_at.strftime("%B %d, %Y") if invoice.created_at else "N/A",
#     }

def generate_invoice_pdf(invoice: dict):

    template = templates.get_template(
        "invoice.html"
    )

    html_content = template.render(
        invoice=invoice,
        logo_path=f"file://{BASE_DIR}/assets/logo.png"
    )

    pdf_buffer = BytesIO()

    HTML(
        string=html_content
    ).write_pdf(pdf_buffer)

    pdf_buffer.seek(0)

    return pdf_buffer