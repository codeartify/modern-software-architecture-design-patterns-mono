from uuid import uuid4

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.managing_plans.shared.plan_entity import PlanOrmModel
from workshop_api.fitness.managing_plans.shared.plan_response import PlanResponse
from workshop_api.fitness.managing_plans.shared.plan_upsert_request import PlanUpsertRequest

router = APIRouter(prefix="/api/plans", tags=["plan"])


@router.post(
    "",
    response_model=PlanResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_plan(
    request: PlanUpsertRequest,
    response: Response,
    session: Session = Depends(get_db_session),
) -> PlanResponse:
    plan = PlanOrmModel(
        id=str(uuid4()),
        title=request.title,
        description=request.description,
        duration_in_months=request.duration_in_months,
        price=request.price,
    )

    session.add(plan)
    session.commit()
    session.refresh(plan)

    created = PlanResponse.from_entity(plan)
    response.headers["Location"] = f"/api/plans/{created.id}"
    return created
