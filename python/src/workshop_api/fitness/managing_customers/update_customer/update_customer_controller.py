from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.managing_customers.shared.customer_entity import CustomerOrmModel
from workshop_api.fitness.managing_customers.shared.customer_response import CustomerResponse
from workshop_api.fitness.managing_customers.shared.customer_upsert_request import (
    CustomerUpsertRequest,
)

router = APIRouter(prefix="/api/customers", tags=["customer"])


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    response_model_by_alias=True,
)
def update_customer(
    customer_id: UUID,
    request: CustomerUpsertRequest,
    session: Session = Depends(get_db_session),
) -> CustomerResponse:
    customer = session.get(CustomerOrmModel, str(customer_id))
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} was not found",
        )

    customer.name = request.name
    customer.date_of_birth = request.date_of_birth
    customer.email_address = request.email_address
    session.commit()
    session.refresh(customer)
    return CustomerResponse.from_entity(customer)
