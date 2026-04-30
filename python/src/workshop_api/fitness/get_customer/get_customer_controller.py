from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.shared.customer_entity import CustomerOrmModel
from workshop_api.fitness.shared.customer_response import CustomerResponse

router = APIRouter(prefix="/api/customers", tags=["customer"])


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    response_model_by_alias=True,
)
def get_customer(
    customer_id: UUID,
    session: Session = Depends(get_db_session),
) -> CustomerResponse:
    customer = session.get(CustomerOrmModel, str(customer_id))
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} was not found",
        )

    return CustomerResponse.from_entity(customer)
