from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.shared.plan_entity import PlanOrmModel
from workshop_api.fitness.shared.plan_response import PlanResponse
from workshop_api.fitness.shared.plan_upsert_request import PlanUpsertRequest

router = APIRouter(prefix="/api/plans", tags=["plan"])


@router.put(
    "/{plan_id}",
    response_model=PlanResponse,
    response_model_by_alias=True,
)
def update_plan(
    plan_id: UUID,
    request: PlanUpsertRequest,
    session: Session = Depends(get_db_session),
) -> PlanResponse:
    plan = session.get(PlanOrmModel, str(plan_id))
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} was not found",
        )

    plan.title = request.title
    plan.description = request.description
    plan.duration_in_months = request.duration_in_months
    plan.price = request.price
    session.commit()
    session.refresh(plan)
    return PlanResponse.from_entity(plan)
