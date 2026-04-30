from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.shared.customer_entity import CustomerOrmModel

router = APIRouter(prefix="/api/customers", tags=["customer"])


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: UUID,
    session: Session = Depends(get_db_session),
) -> Response:
    customer = session.get(CustomerOrmModel, str(customer_id))
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} was not found",
        )

    session.delete(customer)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
