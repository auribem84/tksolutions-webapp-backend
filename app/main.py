from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, billings, users, services, tickets, organizations, settings
from app.api.routes.admin import organizations, users, invitations, billing
from app.db.session import SessionLocal
from app.db.seed import create_default_org

app = FastAPI(title="Customer Portal API")

# 🌐 CORS FIX REAL
origins = [
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8082",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
    "http://127.0.0.1:8082",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 ROUTERS
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(services.router, prefix="/services", tags=["Services"])
app.include_router(billings.router, prefix="/billing", tags=["Billing"])
app.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(settings.router, prefix="/settings", tags=["Settings"])
app.include_router(organizations.router, prefix="/admin/organizations", tags=["Admin"])
app.include_router(users.router, prefix="/admin/users", tags=["Admin"])
app.include_router(invitations.router, prefix="/admin/invitations", tags=["Admin"])
app.include_router(billing.router, prefix="/admin/billing", tags=["Admin"])

# 🚀 STARTUP
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        create_default_org(db)
        db.commit()
    finally:
        db.close()