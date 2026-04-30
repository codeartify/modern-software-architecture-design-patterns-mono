from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from workshop_api.fitness.business.application.errors import NotFoundError
from workshop_api.fitness.business.application.plan_service import PlanService
from workshop_api.fitness.infrastructure.database import get_db_session
from workshop_api.fitness.infrastructure.plan_repository import PlanRepository
from workshop_api.fitness.presentation.plan_schemas import PlanResponse, PlanUpsertRequest

router = APIRouter(prefix="/api/plans", tags=["plan"])


def get_plan_service(session: Session = Depends(get_db_session)) -> PlanService:
    return PlanService(PlanRepository(session))


@router.get("", response_model=list[PlanResponse], response_model_by_alias=True)
def list_plans(service: PlanService = Depends(get_plan_service)) -> list[PlanResponse]:
    return service.list_plans()


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
    response_model_by_alias=True,
)
def get_plan(
    plan_id: UUID,
    service: PlanService = Depends(get_plan_service),
) -> PlanResponse:
    try:
        return service.get_plan(plan_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post(
    "",
    response_model=PlanResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_plan(
    request: PlanUpsertRequest,
    response: Response,
    service: PlanService = Depends(get_plan_service),
) -> PlanResponse:
    created = service.create_plan(request)
    response.headers["Location"] = f"/api/plans/{created.id}"
    return created


@router.put(
    "/{plan_id}",
    response_model=PlanResponse,
    response_model_by_alias=True,
)
def update_plan(
    plan_id: UUID,
    request: PlanUpsertRequest,
    service: PlanService = Depends(get_plan_service),
) -> PlanResponse:
    try:
        return service.update_plan(plan_id, request)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: UUID,
    service: PlanService = Depends(get_plan_service),
) -> Response:
    try:
        service.delete_plan(plan_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
