import os
from uuid import UUID

DEFAULT_ORG_ID = UUID(os.getenv("DEFAULT_ORG_ID"))

DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")