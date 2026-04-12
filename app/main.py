from fastapi import FastAPI
from app.api.routes import auth, users, services, billing, tickets, organizations
from app.db.session import SessionLocal
from app.db.seed import create_default_org

app = FastAPI(title="Customer Portal API")

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(services.router, prefix="/services")
app.include_router(billing.router, prefix="/billing")
app.include_router(tickets.router, prefix="/tickets")
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        create_default_org(db)
    finally:
        db.close()