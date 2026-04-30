from typing import Protocol
from uuid import UUID

from workshop_api.fitness.hexagon.inside.port.outbound.plan import Plan


class ForFindingPlans(Protocol):
    def find_plan_by_id(self, plan_id: UUID) -> Plan:
        pass
