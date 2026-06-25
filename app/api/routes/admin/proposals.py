from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import get_current_user, require_default_admin
from app.services.proposal_pdf import (
    generate_solution_proposal_pdf,
    generate_support_proposal_pdf,
)
from app.services.email_service import send_proposal_email

router = APIRouter()


@router.post("/solution")
def send_solution_proposal(
    data: dict,
    user=Depends(require_default_admin),
):
    pdf_bytes = generate_solution_proposal_pdf(data)

    client_name = data.get("client_name", "Client")
    client_email = data.get("client_email", "")
    project_title = data.get("project_title", "Solution Proposal")

    send_proposal_email(
        to_email=client_email,
        subject=f"Solution Proposal: {project_title} — Teknowsolutions, LLC",
        client_name=client_name,
        proposal_type="solution",
        pdf_bytes=pdf_bytes,
        filename=f"TKSolutions_Proposal_{project_title.replace(' ', '_')}.pdf",
    )

    return JSONResponse({"message": "Solution proposal sent successfully"})


@router.post("/support")
def send_support_proposal(
    data: dict,
    user=Depends(require_default_admin),
):
    pdf_bytes = generate_support_proposal_pdf(data)

    client_name = data.get("client_name", "Client")
    client_email = data.get("client_email", "")
    platform_name = data.get("platform_name", "Platform")

    send_proposal_email(
        to_email=client_email,
        subject=f"Support & Maintenance Proposal: {platform_name} — Teknowsolutions, LLC",
        client_name=client_name,
        proposal_type="support",
        pdf_bytes=pdf_bytes,
        filename=f"TKSolutions_Support_Proposal_{platform_name.replace(' ', '_')}.pdf",
    )

    return JSONResponse({"message": "Support proposal sent successfully"})
