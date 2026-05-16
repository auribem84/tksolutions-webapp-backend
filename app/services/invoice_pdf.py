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

def generate_invoice_pdf(invoice):

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