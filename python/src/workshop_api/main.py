from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    first_error = error.errors()[0]
    location = first_error.get("loc", ())
    invalid_value = first_error.get("input")
    message = first_error.get("msg", "Request validation failed")

    if location and location[0] == "path" and len(location) > 1:
        parameter_name = str(location[1])
        camel_case_parameter_name = parameter_name.split("_")[0] + "".join(
            part.capitalize() for part in parameter_name.split("_")[1:]
        )
        if invalid_value is None:
            invalid_value = request.url.path.rsplit("/", 1)[-1]
        message = f"Invalid value for '{camel_case_parameter_name}': {invalid_value}"

    return JSONResponse(
        status_code=400,
        content={
            "status": 400,
            "error": "Bad Request",
            "message": message,
            "path": request.url.path,
        },
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
