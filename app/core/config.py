import os

ENV = os.getenv("ENV", "development")


def get_database_url():
    url = os.getenv("DATABASE_URL")

    if not url:
        # fallback dev
        return "postgresql://postgres:postgres@localhost:5432/portal"

    # fix postgres:// bug
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    return url


DATABASE_URL = get_database_url()

print("ENV:", ENV)
print("DB:", DATABASE_URL)

# Detect external DB (Render, AWS, etc.)
IS_EXTERNAL_DB = ENV == "production"


# =========================
# AUTH
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60