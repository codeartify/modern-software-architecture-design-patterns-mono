from uuid import UUID

from sqlalchemy.orm import Session

from workshop_api.fitness.customer.models import CustomerOrmModel
from workshop_api.fitness.customer.schemas import CustomerResponse, CustomerUpsertRequest
from workshop_api.fitness.errors import NotFoundError


class CustomerService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_customers(self) -> list[CustomerResponse]:
        customers = self.session.query(CustomerOrmModel).order_by(CustomerOrmModel.name).all()
        return [self._to_response(customer) for customer in customers]

    def get_customer(self, customer_id: UUID) -> CustomerResponse:
        return self._to_response(self._load_customer(customer_id))

    def create_customer(self, request: CustomerUpsertRequest) -> CustomerResponse:
        customer = CustomerOrmModel(
            name=request.name,
            date_of_birth=request.date_of_birth,
            email_address=str(request.email_address),
        )
        self.session.add(customer)
        self.session.commit()
        self.session.refresh(customer)
        return self._to_response(customer)

    def update_customer(
        self,
        customer_id: UUID,
        request: CustomerUpsertRequest,
    ) -> CustomerResponse:
        customer = self._load_customer(customer_id)
        customer.name = request.name
        customer.date_of_birth = request.date_of_birth
        customer.email_address = str(request.email_address)
        self.session.commit()
        self.session.refresh(customer)
        return self._to_response(customer)

    def delete_customer(self, customer_id: UUID) -> None:
        customer = self._load_customer(customer_id)
        self.session.delete(customer)
        self.session.commit()

    def _load_customer(self, customer_id: UUID) -> CustomerOrmModel:
        customer = self.session.get(CustomerOrmModel, str(customer_id))
        if customer is None:
            raise NotFoundError(f"Customer {customer_id} was not found")
        return customer

    @staticmethod
    def _to_response(customer: CustomerOrmModel) -> CustomerResponse:
        return CustomerResponse(
            id=customer.id,
            name=customer.name,
            dateOfBirth=customer.date_of_birth,
            emailAddress=customer.email_address,
        )
