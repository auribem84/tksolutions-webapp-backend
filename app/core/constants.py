import os
import uuid

DEFAULT_ORG_ID = uuid.UUID(
    os.getenv("DEFAULT_ORG_ID")
)

DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")