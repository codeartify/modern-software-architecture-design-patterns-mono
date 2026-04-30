from uuid import UUID

from workshop_api.fitness.hexagon.inside.port.outbound.for_finding_plans import (
    ForFindingPlans,
)
from workshop_api.fitness.hexagon.inside.port.outbound.plan import Plan
from workshop_api.fitness.hexagon.inside.port.outbound.plan_not_found_exception import (
    PlanNotFoundException,
)
from workshop_api.fitness.layered.infrastructure.plan_repository import PlanRepository


class JpaPlanRepository(ForFindingPlans):
    def __init__(self, plan_repository: PlanRepository) -> None:
        self.plan_repository = plan_repository

    def find_plan_by_id(self, plan_id: UUID) -> Plan:
        plan_entity = self.plan_repository.find_by_id(plan_id)
        if plan_entity is None:
            raise PlanNotFoundException(f"Plan {plan_id} was not found")

        return Plan(
            id=plan_id,
            price=plan_entity.price,
            duration_in_months=plan_entity.duration_in_months,
            title=plan_entity.title,
        )
