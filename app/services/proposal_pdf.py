from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
import uuid
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

templates = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, "templates"))
)

LOGO_PATH = f"file://{BASE_DIR}/assets/logo.png"


def _short_id() -> str:
    return str(uuid.uuid4()).replace("-", "")[-6:].upper()


def _fmt_date(val: str | None) -> str | None:
    if not val:
        return None
    try:
        return date.fromisoformat(val).strftime("%B %d, %Y")
    except ValueError:
        return val


def generate_solution_proposal_pdf(data: dict) -> bytes:
    line_items = data.get("line_items") or []
    total = sum(float(item.get("amount", 0)) for item in line_items)

    proposal = {
        "short_id": _short_id(),
        "issued_date": date.today().strftime("%B %d, %Y"),
        "client_name": data.get("client_name", ""),
        "client_email": data.get("client_email", ""),
        "project_title": data.get("project_title", ""),
        "executive_summary": data.get("executive_summary", ""),
        "scope_of_work": data.get("scope_of_work", ""),
        "proposed_solution": data.get("proposed_solution", ""),
        "timeline_start": _fmt_date(data.get("timeline_start")),
        "timeline_duration": data.get("timeline_duration", ""),
        "line_items": [
            {"description": i.get("description", ""), "amount": float(i.get("amount", 0))}
            for i in line_items
        ],
        "total": total,
        "payment_terms": data.get("payment_terms", ""),
        "valid_until": _fmt_date(data.get("valid_until")),
        "notes": data.get("notes", ""),
    }

    html = templates.get_template("proposal_solution.html").render(
        proposal=proposal,
        logo_path=LOGO_PATH,
    )

    buf = BytesIO()
    HTML(string=html).write_pdf(buf)
    buf.seek(0)
    return buf.read()


def generate_support_proposal_pdf(data: dict) -> bytes:
    monthly = data.get("monthly_cost")
    annual = data.get("annual_cost")

    proposal = {
        "short_id": _short_id(),
        "issued_date": date.today().strftime("%B %d, %Y"),
        "client_name": data.get("client_name", ""),
        "client_email": data.get("client_email", ""),
        "platform_name": data.get("platform_name", ""),
        "platform_description": data.get("platform_description", ""),
        "support_tier": data.get("support_tier", ""),
        "services_included": data.get("services_included", ""),
        "response_time_sla": data.get("response_time_sla", ""),
        "monthly_cost": float(monthly) if monthly else None,
        "annual_cost": float(annual) if annual else None,
        "contract_duration": data.get("contract_duration", ""),
        "start_date": _fmt_date(data.get("start_date")),
        "notes": data.get("notes", ""),
    }

    html = templates.get_template("proposal_support.html").render(
        proposal=proposal,
        logo_path=LOGO_PATH,
    )

    buf = BytesIO()
    HTML(string=html).write_pdf(buf)
    buf.seek(0)
    return buf.read()
