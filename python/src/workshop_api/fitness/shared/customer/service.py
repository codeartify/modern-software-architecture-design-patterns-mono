from sqlalchemy.orm import Session

from workshop_api.fitness.shared.customer.models import SharedCustomerOrmModel
from workshop_api.fitness.shared.customer.schemas import (
    SharedCustomerResponse,
    SharedCustomerUpsertRequest,
)
from workshop_api.fitness.shared.errors import NotFoundError


class SharedCustomerService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_customers(self) -> list[SharedCustomerResponse]:
        customers = self.session.query(SharedCustomerOrmModel).order_by(SharedCustomerOrmModel.name).all()
        return [self._to_response(customer) for customer in customers]

    def get_customer(self, customer_id: str) -> SharedCustomerResponse:
        return self._to_response(self._load_customer(customer_id))

    def create_customer(self, request: SharedCustomerUpsertRequest) -> SharedCustomerResponse:
        customer = SharedCustomerOrmModel(
            name=request.name,
            date_of_birth=request.date_of_birth,
            email_address=str(request.email_address),
        )
        self.session.add(customer)
        self.session.commit()
        self.session.refresh(customer)
        return self._to_response(customer)

    def update_customer(self, customer_id: str, request: SharedCustomerUpsertRequest) -> SharedCustomerResponse:
        customer = self._load_customer(customer_id)
        customer.name = request.name
        customer.date_of_birth = request.date_of_birth
        customer.email_address = str(request.email_address)
        self.session.commit()
        self.session.refresh(customer)
        return self._to_response(customer)

    def delete_customer(self, customer_id: str) -> None:
        customer = self._load_customer(customer_id)
        self.session.delete(customer)
        self.session.commit()

    def _load_customer(self, customer_id: str) -> SharedCustomerOrmModel:
        customer = self.session.get(SharedCustomerOrmModel, customer_id)
        if customer is None:
            raise NotFoundError(f"Customer {customer_id} was not found")
        return customer

    @staticmethod
    def _to_response(customer: SharedCustomerOrmModel) -> SharedCustomerResponse:
        return SharedCustomerResponse(
            id=customer.id,
            name=customer.name,
            dateOfBirth=customer.date_of_birth,
            emailAddress=customer.email_address,
        )
