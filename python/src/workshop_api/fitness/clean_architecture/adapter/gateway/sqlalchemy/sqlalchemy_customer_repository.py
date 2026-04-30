from uuid import UUID

from workshop_api.fitness.layered.infrastructure.customer_repository import CustomerRepository

from ....entity import Customer
from ....use_case.port.outbound import (
    CustomerNotFoundException,
    ForFindingCustomers,
)


class SqlAlchemyCustomerRepository(ForFindingCustomers):
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    def find_customer_by_id(self, customer_id: UUID) -> Customer:
        customer_entity = self.customer_repository.find_by_id(customer_id)
        if customer_entity is None:
            raise CustomerNotFoundException(f"Customer {customer_id} was not found")

        return Customer(
            id=customer_entity.id,
            date_of_birth=customer_entity.date_of_birth,
            email_address=customer_entity.email_address,
        )
