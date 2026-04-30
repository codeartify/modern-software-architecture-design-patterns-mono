from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.shared.plan_entity import PlanOrmModel
from workshop_api.fitness.shared.plan_response import PlanResponse

router = APIRouter(prefix="/api/plans", tags=["plan"])


@router.get("", response_model=list[PlanResponse], response_model_by_alias=True)
def list_plans(session: Session = Depends(get_db_session)) -> list[PlanResponse]:
    plans = session.query(PlanOrmModel).order_by(PlanOrmModel.title).all()
    return [PlanResponse.from_entity(plan) for plan in plans]
