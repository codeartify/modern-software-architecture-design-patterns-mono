from uuid import UUID

from workshop_api.fitness.hexagon.inside.port.outbound.customer import Customer
from workshop_api.fitness.hexagon.inside.port.outbound.customer_not_found_exception import (
    CustomerNotFoundException,
)
from workshop_api.fitness.hexagon.inside.port.outbound.for_finding_customers import (
    ForFindingCustomers,
)
from workshop_api.fitness.layered.infrastructure.customer_repository import CustomerRepository


class SqlAlchemyCustomerRepository(ForFindingCustomers):
    def __init__(self, customer_repository: CustomerRepository) -> None:
        self.customer_repository = customer_repository

    def find_customer_by_id(self, customer_id: UUID) -> Customer:
        customer_entity = self.customer_repository.find_by_id(customer_id)
        if customer_entity is None:
            raise CustomerNotFoundException(f"Customer {customer_id} was not found")

        return Customer(
            date_of_birth=customer_entity.date_of_birth,
            email_address=customer_entity.email_address,
        )
