from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from workshop_api.fitness.shared.customer.database import get_db_session
from workshop_api.fitness.shared.customer.schemas import (
    SharedCustomerResponse,
    SharedCustomerUpsertRequest,
)
from workshop_api.fitness.shared.customer.service import SharedCustomerService
from workshop_api.fitness.shared.errors import NotFoundError

router = APIRouter(prefix="/api/shared/customers", tags=["shared-customer"])


def get_customer_service(session: Session = Depends(get_db_session)) -> SharedCustomerService:
    return SharedCustomerService(session)


@router.get("", response_model=list[SharedCustomerResponse], response_model_by_alias=True)
def list_customers(
    service: SharedCustomerService = Depends(get_customer_service),
) -> list[SharedCustomerResponse]:
    return service.list_customers()


@router.get(
    "/{customer_id}",
    response_model=SharedCustomerResponse,
    response_model_by_alias=True,
)
def get_customer(
    customer_id: str,
    service: SharedCustomerService = Depends(get_customer_service),
) -> SharedCustomerResponse:
    try:
        return service.get_customer(customer_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post(
    "",
    response_model=SharedCustomerResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    request: SharedCustomerUpsertRequest,
    response: Response,
    service: SharedCustomerService = Depends(get_customer_service),
) -> SharedCustomerResponse:
    created = service.create_customer(request)
    response.headers["Location"] = f"/api/shared/customers/{created.id}"
    return created


@router.put(
    "/{customer_id}",
    response_model=SharedCustomerResponse,
    response_model_by_alias=True,
)
def update_customer(
    customer_id: str,
    request: SharedCustomerUpsertRequest,
    service: SharedCustomerService = Depends(get_customer_service),
) -> SharedCustomerResponse:
    try:
        return service.update_customer(customer_id, request)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: str,
    service: SharedCustomerService = Depends(get_customer_service),
) -> Response:
    try:
        service.delete_customer(customer_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
