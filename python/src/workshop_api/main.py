from fastapi import FastAPI

from workshop_api.fitness.shared.customer.database import init_db
from workshop_api.fitness.shared.customer.router import router as shared_customer_router
from workshop_api.fitness.shared.plan.router import router as shared_plan_router

app = FastAPI(title="Architecture Python API")
init_db()
app.include_router(shared_customer_router)
app.include_router(shared_plan_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
