from uuid import uuid4

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.managing_customers.shared.customer_entity import CustomerOrmModel
from workshop_api.fitness.managing_customers.shared.customer_response import CustomerResponse
from workshop_api.fitness.managing_customers.shared.customer_upsert_request import (
    CustomerUpsertRequest,
)

router = APIRouter(prefix="/api/customers", tags=["customer"])


@router.post(
    "",
    response_model=CustomerResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    request: CustomerUpsertRequest,
    response: Response,
    session: Session = Depends(get_db_session),
) -> CustomerResponse:
    customer = CustomerOrmModel(
        id=str(uuid4()),
        name=request.name,
        date_of_birth=request.date_of_birth,
        email_address=request.email_address,
    )

    session.add(customer)
    session.commit()
    session.refresh(customer)

    created = CustomerResponse.from_entity(customer)
    response.headers["Location"] = f"/api/customers/{created.id}"
    return created
