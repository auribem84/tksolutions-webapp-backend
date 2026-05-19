# app/services/email_service.py

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import boto3
import os

ses = boto3.client(
    "ses",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
)


def send_invitation_email(to_email: str, invite_link: str):
    ses.send_email(
        Source=os.getenv("SES_FROM_EMAIL"),
        Destination={
            "ToAddresses": [to_email]
        },
        Message={
            "Subject": {
                "Data": "You're invited to Teknow Solutions Portal"
            },
            "Body": {
                "Html": {
                    "Data": f"""
                    <h2>Welcome</h2>

                    <p>You have been invited to join the portal.</p>

                    <p>
                        <a href="{invite_link}">
                            Accept Invitation
                        </a>
                    </p>
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

    ses.send_raw_email(
        Source=os.getenv("SES_FROM_EMAIL"),
        Destinations=[recipient_email],
        RawMessage={
            "Data": message.as_string()
        }
    )