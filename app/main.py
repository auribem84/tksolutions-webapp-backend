from fastapi import FastAPI
from app.api.routes import auth, users, services, billing, tickets

app = FastAPI(title="Customer Portal API")

app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(services.router, prefix="/services")
app.include_router(billing.router, prefix="/billing")
app.include_router(tickets.router, prefix="/tickets")