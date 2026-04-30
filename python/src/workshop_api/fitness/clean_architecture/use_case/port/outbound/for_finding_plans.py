from typing import Protocol
from uuid import UUID

from workshop_api.fitness.clean_architecture.entity.plan import Plan


class ForFindingPlans(Protocol):
    def find_plan_by_id(self, plan_id: UUID) -> Plan:
        pass
