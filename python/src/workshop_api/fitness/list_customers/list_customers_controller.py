from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.shared.customer_entity import CustomerOrmModel
from workshop_api.fitness.shared.customer_response import CustomerResponse

router = APIRouter(prefix="/api/customers", tags=["customer"])


@router.get("", response_model=list[CustomerResponse], response_model_by_alias=True)
def list_customers(session: Session = Depends(get_db_session)) -> list[CustomerResponse]:
    customers = session.query(CustomerOrmModel).order_by(CustomerOrmModel.name).all()
    return [CustomerResponse.from_entity(customer) for customer in customers]
