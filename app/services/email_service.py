# app/services/email_service.py

import boto3
import os

ses = boto3.client(
    "ses",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
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