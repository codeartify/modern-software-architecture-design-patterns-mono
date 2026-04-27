from fastapi import FastAPI

from workshop_api.fitness.customer.database import init_db
from workshop_api.fitness.customer.router import router as customer_router
from workshop_api.fitness.external_invoice_provider.router import (
    router as external_invoice_provider_router,
)
from workshop_api.fitness.membership.exercise00_mixed.router import (
    router as e00_membership_router,
)
from workshop_api.fitness.plan.router import router as plan_router

app = FastAPI(title="Architecture Python API")
init_db()
app.include_router(customer_router)
app.include_router(external_invoice_provider_router)
app.include_router(e00_membership_router)
app.include_router(plan_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
