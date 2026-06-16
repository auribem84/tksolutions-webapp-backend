import requests
from app.core.config import SLACK_WEBHOOK_URL


def notify_new_ticket(ref: str, subject: str, priority: str, created_by: str):
    if not SLACK_WEBHOOK_URL:
        return

    priority_emoji = {"high": ":red_circle:", "medium": ":large_yellow_circle:", "low": ":large_green_circle:"}.get(priority, ":white_circle:")

    payload = {
        "text": (
            f":ticket: *New Support Ticket* — `{ref}`\n"
            f"*Subject:* {subject}\n"
            f"*Priority:* {priority_emoji} {priority.capitalize()}\n"
            f"*Submitted by:* {created_by}"
        )
    }

    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
    except Exception:
        pass
