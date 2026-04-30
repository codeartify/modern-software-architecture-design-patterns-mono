from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from workshop_api.external_invoice_provider.invoice_provider_controller import (
    router as external_invoice_provider_router,
)
from workshop_api.fitness.database import init_db
from workshop_api.fitness.managing_customers.create_customer import create_customer_controller
from workshop_api.fitness.managing_customers.delete_customer import delete_customer_controller
from workshop_api.fitness.managing_customers.get_customer import get_customer_controller
from workshop_api.fitness.managing_customers.list_customers import list_customers_controller
from workshop_api.fitness.managing_customers.update_customer import update_customer_controller
from workshop_api.fitness.managing_memberships.activate_membership import (
    activate_membership_controller,
)
from workshop_api.fitness.managing_memberships.cancel_membership import cancel_membership_controller
from workshop_api.fitness.managing_memberships.extend_membership import extend_membership_controller
from workshop_api.fitness.managing_memberships.get_membership import get_membership_controller
from workshop_api.fitness.managing_memberships.handle_payment_received import (
    handle_payment_received_controller,
)
from workshop_api.fitness.managing_memberships.list_memberships import list_membership_controller
from workshop_api.fitness.managing_memberships.pause_membership import pause_membership_controller
from workshop_api.fitness.managing_memberships.resume_membership import resume_membership_controller
from workshop_api.fitness.managing_memberships.suspend_membership import (
    suspend_membership_controller,
)
from workshop_api.fitness.managing_plans.create_plan import create_plan_controller
from workshop_api.fitness.managing_plans.delete_plan import delete_plan_controller
from workshop_api.fitness.managing_plans.get_plan import get_plan_controller
from workshop_api.fitness.managing_plans.list_plans import list_plans_controller
from workshop_api.fitness.managing_plans.update_plan import update_plan_controller

app = FastAPI(title="Architecture Python API")
init_db()
app.include_router(external_invoice_provider_router)
app.include_router(create_customer_controller.router)
app.include_router(list_customers_controller.router)
app.include_router(get_customer_controller.router)
app.include_router(update_customer_controller.router)
app.include_router(delete_customer_controller.router)
app.include_router(create_plan_controller.router)
app.include_router(list_plans_controller.router)
app.include_router(get_plan_controller.router)
app.include_router(update_plan_controller.router)
app.include_router(delete_plan_controller.router)
app.include_router(list_membership_controller.router)
app.include_router(activate_membership_controller.router)
app.include_router(handle_payment_received_controller.router)
app.include_router(suspend_membership_controller.router)
app.include_router(pause_membership_controller.router)
app.include_router(resume_membership_controller.router)
app.include_router(cancel_membership_controller.router)
app.include_router(extend_membership_controller.router)
app.include_router(get_membership_controller.router)


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
