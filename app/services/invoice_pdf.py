from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

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
            "address1": profile.address1 if profile else "",
            "address2": profile.address2 if profile else "",
            "city": profile.city if profile else "",
            "state": profile.state if profile else "",
            "zip": profile.zip if profile else "",
            "phone": profile.phone if profile else "",
            "email": profile.email if profile else "",
        }
    }

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