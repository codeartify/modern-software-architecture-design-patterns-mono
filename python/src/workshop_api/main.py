from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from workshop_api.external_invoice_provider.invoice_provider_controller import (
    router as external_invoice_provider_router,
)
from workshop_api.fitness.activate_membership.activate_membership_controller import (
    router as activate_membership_router,
)
from workshop_api.fitness.cancel_membership.cancel_membership_controller import (
    router as cancel_membership_router,
)
from workshop_api.fitness.create_customer.create_customer_controller import (
    router as create_customer_router,
)
from workshop_api.fitness.create_plan.create_plan_controller import router as create_plan_router
from workshop_api.fitness.database import init_db
from workshop_api.fitness.delete_customer.delete_customer_controller import (
    router as delete_customer_router,
)
from workshop_api.fitness.delete_plan.delete_plan_controller import router as delete_plan_router
from workshop_api.fitness.extend_membership.extend_membership_controller import (
    router as extend_membership_router,
)
from workshop_api.fitness.get_customer.get_customer_controller import (
    router as get_customer_router,
)
from workshop_api.fitness.get_membership.get_membership_controller import (
    router as get_membership_router,
)
from workshop_api.fitness.get_plan.get_plan_controller import router as get_plan_router
from workshop_api.fitness.handle_payment_received.handle_payment_received_controller import (
    router as handle_payment_received_router,
)
from workshop_api.fitness.list_customers.list_customers_controller import (
    router as list_customers_router,
)
from workshop_api.fitness.list_memberships.list_membership_controller import (
    router as list_memberships_router,
)
from workshop_api.fitness.list_plans.list_plans_controller import router as list_plans_router
from workshop_api.fitness.pause_membership.pause_membership_controller import (
    router as pause_membership_router,
)
from workshop_api.fitness.resume_membership.resume_membership_controller import (
    router as resume_membership_router,
)
from workshop_api.fitness.suspend_membership.suspend_membership_controller import (
    router as suspend_membership_router,
)
from workshop_api.fitness.update_customer.update_customer_controller import (
    router as update_customer_router,
)
from workshop_api.fitness.update_plan.update_plan_controller import router as update_plan_router

app = FastAPI(title="Architecture Python API")
init_db()
app.include_router(external_invoice_provider_router)
app.include_router(create_customer_router)
app.include_router(list_customers_router)
app.include_router(get_customer_router)
app.include_router(update_customer_router)
app.include_router(delete_customer_router)
app.include_router(create_plan_router)
app.include_router(list_plans_router)
app.include_router(get_plan_router)
app.include_router(update_plan_router)
app.include_router(delete_plan_router)
app.include_router(list_memberships_router)
app.include_router(activate_membership_router)
app.include_router(handle_payment_received_router)
app.include_router(suspend_membership_router)
app.include_router(pause_membership_router)
app.include_router(resume_membership_router)
app.include_router(cancel_membership_router)
app.include_router(extend_membership_router)
app.include_router(get_membership_router)


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
