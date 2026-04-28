from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from workshop_api.fitness.customer.database import get_db_session
from workshop_api.fitness.customer.schemas import CustomerResponse, CustomerUpsertRequest
from workshop_api.fitness.customer.service import CustomerService
from workshop_api.fitness.errors import NotFoundError

router = APIRouter(prefix="/api/customers", tags=["customer"])


def get_customer_service(session: Session = Depends(get_db_session)) -> CustomerService:
    return CustomerService(session)


@router.get("", response_model=list[CustomerResponse], response_model_by_alias=True)
def list_customers(
    service: CustomerService = Depends(get_customer_service),
) -> list[CustomerResponse]:
    return service.list_customers()


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    response_model_by_alias=True,
)
def get_customer(
    customer_id: UUID,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    try:
        return service.get_customer(customer_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post(
    "",
    response_model=CustomerResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    request: CustomerUpsertRequest,
    response: Response,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    created = service.create_customer(request)
    response.headers["Location"] = f"/api/customers/{created.id}"
    return created


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    response_model_by_alias=True,
)
def update_customer(
    customer_id: UUID,
    request: CustomerUpsertRequest,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    try:
        return service.update_customer(customer_id, request)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: UUID,
    service: CustomerService = Depends(get_customer_service),
) -> Response:
    try:
        service.delete_customer(customer_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
