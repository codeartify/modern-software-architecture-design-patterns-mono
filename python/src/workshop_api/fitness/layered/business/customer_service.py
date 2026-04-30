from uuid import UUID

from workshop_api.fitness.layered.business.errors import NotFoundError
from workshop_api.fitness.layered.infrastructure.customer_entity import CustomerOrmModel
from workshop_api.fitness.layered.infrastructure.customer_repository import CustomerRepository
from workshop_api.fitness.layered.presentation.customer_schemas import (
    CustomerResponse,
    CustomerUpsertRequest,
)


class CustomerService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def list_customers(self) -> list[CustomerResponse]:
        customers = sorted(self.repository.find_all(), key=lambda customer: customer.name)
        return [self._to_response(customer) for customer in customers]

    def get_customer(self, customer_id: UUID) -> CustomerResponse:
        return self._to_response(self._load_customer(customer_id))

    def create_customer(self, request: CustomerUpsertRequest) -> CustomerResponse:
        customer = CustomerOrmModel(
            name=request.name,
            date_of_birth=request.date_of_birth,
            email_address=str(request.email_address),
        )
        return self._to_response(self.repository.save(customer))

    def update_customer(
        self,
        customer_id: UUID,
        request: CustomerUpsertRequest,
    ) -> CustomerResponse:
        customer = self._load_customer(customer_id)
        customer.name = request.name
        customer.date_of_birth = request.date_of_birth
        customer.email_address = str(request.email_address)
        return self._to_response(self.repository.save(customer))

    def delete_customer(self, customer_id: UUID) -> None:
        customer = self._load_customer(customer_id)
        self.repository.delete(customer)

    def _load_customer(self, customer_id: UUID) -> CustomerOrmModel:
        customer = self.repository.find_by_id(customer_id)
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
