from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from workshop_api.fitness.customer.database import init_db
from workshop_api.fitness.customer.router import router as customer_router
from workshop_api.fitness.external_invoice_provider.router import (
    router as external_invoice_provider_router,
)
from workshop_api.fitness.membership.router import (
    router as membership_router,
)
from workshop_api.fitness.plan.router import router as plan_router

app = FastAPI(title="Architecture Python API")
init_db()
app.include_router(customer_router)
app.include_router(external_invoice_provider_router)
app.include_router(membership_router)
app.include_router(plan_router)


def _api_error_response(
    request: Request,
    status_code: int,
    message: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_code,
            "error": HTTPStatus(status_code).phrase,
            "message": message,
            "path": request.url.path,
        },
    )


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

    return _api_error_response(request, 400, message)


@app.exception_handler(HTTPException)
async def handle_http_exception(
    request: Request,
    error: HTTPException,
) -> JSONResponse:
    message = str(error.detail) if error.detail else HTTPStatus(error.status_code).phrase
    return _api_error_response(request, error.status_code, message)


@app.exception_handler(Exception)
async def handle_unexpected_exception(
    request: Request,
    _: Exception,
) -> JSONResponse:
    return _api_error_response(request, 500, "Internal server error")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
