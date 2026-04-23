# app/services/email_service.py

import boto3

ses = boto3.client("ses", region_name="us-east-1")

def send_email(to: str, subject: str, body: str):
    ses.send_email(
        Source="noreply@yourapp.com",
        Destination={"ToAddresses": [to]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    )