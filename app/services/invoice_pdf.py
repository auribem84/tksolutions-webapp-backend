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

def serialize_invoice(invoice):
    return {
        "id": str(invoice.id),
        "short_id": str(invoice.id).replace("-", "")[:8].lower(),

        "amount": float(invoice.amount or 0),
        "description": invoice.description or "",
        "status": invoice.status,

        "due_date": invoice.due_date.strftime("%B %d, %Y") if invoice.due_date else "N/A",
        "created_at": invoice.created_at.strftime("%B %d, %Y") if invoice.created_at else "N/A",
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