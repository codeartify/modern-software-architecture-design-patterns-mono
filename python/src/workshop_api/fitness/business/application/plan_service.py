from uuid import UUID

from workshop_api.fitness.business.application.errors import NotFoundError
from workshop_api.fitness.infrastructure.plan_entity import PlanOrmModel
from workshop_api.fitness.infrastructure.plan_repository import PlanRepository
from workshop_api.fitness.presentation.plan_schemas import PlanResponse, PlanUpsertRequest


class PlanService:
    def __init__(self, repository: PlanRepository) -> None:
        self.repository = repository

    def list_plans(self) -> list[PlanResponse]:
        plans = sorted(self.repository.find_all(), key=lambda plan: plan.title)
        return [self._to_response(plan) for plan in plans]

    def get_plan(self, plan_id: UUID) -> PlanResponse:
        return self._to_response(self._load_plan(plan_id))

    def create_plan(self, request: PlanUpsertRequest) -> PlanResponse:
        plan = PlanOrmModel(
            title=request.title,
            description=request.description,
            duration_in_months=request.duration_in_months,
            price=request.price,
        )
        return self._to_response(self.repository.save(plan))

    def update_plan(self, plan_id: UUID, request: PlanUpsertRequest) -> PlanResponse:
        plan = self._load_plan(plan_id)
        plan.title = request.title
        plan.description = request.description
        plan.duration_in_months = request.duration_in_months
        plan.price = request.price
        return self._to_response(self.repository.save(plan))

    def delete_plan(self, plan_id: UUID) -> None:
        plan = self._load_plan(plan_id)
        self.repository.delete(plan)

    def _load_plan(self, plan_id: UUID) -> PlanOrmModel:
        plan = self.repository.find_by_id(plan_id)
        if plan is None:
            raise NotFoundError(f"Plan {plan_id} was not found")
        return plan

    @staticmethod
    def _to_response(plan: PlanOrmModel) -> PlanResponse:
        return PlanResponse(
            id=plan.id,
            title=plan.title,
            description=plan.description,
            durationInMonths=plan.duration_in_months,
            price=plan.price,
        )
