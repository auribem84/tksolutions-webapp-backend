# app/services/email_service.py

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from botocore.exceptions import ClientError
from jinja2 import Environment, FileSystemLoader

import boto3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

templates = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, "templates"))
)

ses = boto3.client(
    "ses",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
)


def send_proposal_email(
    to_email: str,
    subject: str,
    client_name: str,
    proposal_type: str,
    pdf_bytes: bytes,
    filename: str,
):
    if proposal_type == "support":
        body_html = f"""
        <p>Dear {client_name},</p>
        <p>Please find attached your <strong>Support &amp; Maintenance Proposal</strong> from Teknowsolutions, LLC.</p>
        <p>Please review the attached document and feel free to reach out with any questions.</p>
        <p>Best regards,<br/>Teknowsolutions, LLC</p>
        """
    else:
        body_html = f"""
        <p>Dear {client_name},</p>
        <p>Please find attached your <strong>Solution Proposal</strong> from Teknowsolutions, LLC.</p>
        <p>Please review the attached document and feel free to reach out with any questions.</p>
        <p>Best regards,<br/>Teknowsolutions, LLC</p>
        """

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = os.getenv("SES_FROM_EMAIL")
    message["To"] = to_email

    message.attach(MIMEText(body_html, "html"))

    attachment = MIMEApplication(pdf_bytes)
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    message.attach(attachment)

    ses.send_raw_email(
        Source=os.getenv("SES_FROM_EMAIL"),
        Destinations=[to_email],
        RawMessage={"Data": message.as_string()},
    )


def send_onboarding_invite_email(to_email: str, form_link: str):
    html = templates.get_template("email_onboarding_invite.html").render(
        form_link=form_link,
    )

    ses.send_email(
        Source=os.getenv("SES_FROM_EMAIL"),
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": "Action Required: Complete Your Client Discovery Form — Teknowsolutions"},
            "Body": {"Html": {"Data": html}},
        },
    )


def send_invitation_email(to_email: str, invite_link: str):
    html = templates.get_template("email_invitation.html").render(
        invite_link=invite_link,
    )

    ses.send_email(
        Source=os.getenv("SES_FROM_EMAIL"),
        Destination={
            "ToAddresses": [to_email]
        },
        Message={
            "Subject": {
                "Data": "You're invited to Teknowsolutions Customer Portal"
            },
            "Body": {
                "Html": {
                    "Data": html
                }
            }
        }
    )

def send_welcome_email(to_email: str, first_name: str):
    frontend_url = os.getenv("FRONTEND_URL", "https://my.teknowsolutions.com")

    html = templates.get_template("email_welcome.html").render(
        first_name=first_name,
        login_link=f"{frontend_url}/login",
    )

    ses.send_email(
        Source=os.getenv("SES_FROM_EMAIL"),
        Destination={
            "ToAddresses": [to_email]
        },
        Message={
            "Subject": {
                "Data": "Welcome to Teknowsolutions, LLC Customer Portal"
            },
            "Body": {
                "Html": {
                    "Data": html
                }
            }
        }
    )


def send_password_reset_email(to_email: str, reset_link: str):
    ses.send_email(
        Source=os.getenv("SES_FROM_EMAIL"),
        Destination={
            "ToAddresses": [to_email]
        },
        Message={
            "Subject": {
                "Data": "Reset your Teknowsolutions password"
            },
            "Body": {
                "Html": {
                    "Data": f"""
                    <h2>Password Reset</h2>

                    <p>We received a request to reset your password.</p>

                    <p>This link will expire in 30 minutes.</p>

                    <p>
                        <a href="{reset_link}">
                            Reset Password
                        </a>
                    </p>

                    <p>If you didn't request this, you can safely ignore this email.</p>
                    """
                }
            }
        }
    )


def send_invoice_email(
    recipient_email: str,
    subject: str,
    body_html: str,
    pdf_bytes: bytes,
    filename: str,
):

    message = MIMEMultipart()

    message["Subject"] = subject
    message["From"] = os.getenv("SES_FROM_EMAIL")
    message["To"] = recipient_email

    # EMAIL BODY
    body_part = MIMEText(body_html, "html")
    message.attach(body_part)

    # PDF ATTACHMENT
    attachment = MIMEApplication(pdf_bytes)

    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=filename
    )

    message.attach(attachment)

    try:
        response = ses.send_raw_email(
            Source=os.getenv("SES_FROM_EMAIL"),
            Destinations=[recipient_email],
            RawMessage={
                "Data": message.as_string(),
            }
        )

        print(
            "EMAIL SENT:",
            response["MessageId"]
        )

        return {
            "success": True,
            "message_id": response["MessageId"]
        }

    except ClientError as e:
        print(
            "EMAIL ERROR:",
            e.response["Error"]["Message"]
        )

        return {
            "success": False,
            "error": e.response["Error"]["Message"]
        }