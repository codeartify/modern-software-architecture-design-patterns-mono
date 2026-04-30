from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.managing_plans.shared.plan_entity import PlanOrmModel
from workshop_api.fitness.managing_plans.shared.plan_response import PlanResponse

router = APIRouter(prefix="/api/plans", tags=["plan"])


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
    response_model_by_alias=True,
)
def get_plan(
    plan_id: UUID,
    session: Session = Depends(get_db_session),
) -> PlanResponse:
    plan = session.get(PlanOrmModel, str(plan_id))
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} was not found",
        )

    return PlanResponse.from_entity(plan)
