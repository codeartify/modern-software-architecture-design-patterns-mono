from sqlalchemy.orm import Session

from workshop_api.fitness.shared.errors import NotFoundError
from workshop_api.fitness.shared.plan.models import SharedPlanOrmModel
from workshop_api.fitness.shared.plan.schemas import SharedPlanResponse, SharedPlanUpsertRequest


class SharedPlanService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_plans(self) -> list[SharedPlanResponse]:
        plans = self.session.query(SharedPlanOrmModel).order_by(SharedPlanOrmModel.title).all()
        return [self._to_response(plan) for plan in plans]

    def get_plan(self, plan_id: str) -> SharedPlanResponse:
        return self._to_response(self._load_plan(plan_id))

    def create_plan(self, request: SharedPlanUpsertRequest) -> SharedPlanResponse:
        plan = SharedPlanOrmModel(
            title=request.title,
            description=request.description,
            duration_in_months=request.duration_in_months,
            price=request.price,
        )
        self.session.add(plan)
        self.session.commit()
        self.session.refresh(plan)
        return self._to_response(plan)

    def update_plan(self, plan_id: str, request: SharedPlanUpsertRequest) -> SharedPlanResponse:
        plan = self._load_plan(plan_id)
        plan.title = request.title
        plan.description = request.description
        plan.duration_in_months = request.duration_in_months
        plan.price = request.price
        self.session.commit()
        self.session.refresh(plan)
        return self._to_response(plan)

    def delete_plan(self, plan_id: str) -> None:
        plan = self._load_plan(plan_id)
        self.session.delete(plan)
        self.session.commit()

    def _load_plan(self, plan_id: str) -> SharedPlanOrmModel:
        plan = self.session.get(SharedPlanOrmModel, plan_id)
        if plan is None:
            raise NotFoundError(f"Plan {plan_id} was not found")
        return plan

    @staticmethod
    def _to_response(plan: SharedPlanOrmModel) -> SharedPlanResponse:
        return SharedPlanResponse(
            id=plan.id,
            title=plan.title,
            description=plan.description,
            durationInMonths=plan.duration_in_months,
            price=plan.price,
        )
