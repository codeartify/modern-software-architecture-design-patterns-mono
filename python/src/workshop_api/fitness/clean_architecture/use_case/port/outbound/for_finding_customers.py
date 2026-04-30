from typing import Protocol
from uuid import UUID

from workshop_api.fitness.clean_architecture.entity.customer import Customer


class ForFindingCustomers(Protocol):
    def find_customer_by_id(self, customer_id: UUID) -> Customer:
        pass
