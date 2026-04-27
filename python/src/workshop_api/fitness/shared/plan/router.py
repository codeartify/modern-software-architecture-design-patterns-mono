from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from workshop_api.fitness.shared.customer.database import get_db_session
from workshop_api.fitness.shared.errors import NotFoundError
from workshop_api.fitness.shared.plan.schemas import SharedPlanResponse, SharedPlanUpsertRequest
from workshop_api.fitness.shared.plan.service import SharedPlanService

router = APIRouter(prefix="/api/shared/plans", tags=["shared-plan"])


def get_plan_service(session: Session = Depends(get_db_session)) -> SharedPlanService:
    return SharedPlanService(session)


@router.get("", response_model=list[SharedPlanResponse], response_model_by_alias=True)
def list_plans(service: SharedPlanService = Depends(get_plan_service)) -> list[SharedPlanResponse]:
    return service.list_plans()


@router.get(
    "/{plan_id}",
    response_model=SharedPlanResponse,
    response_model_by_alias=True,
)
def get_plan(
    plan_id: str,
    service: SharedPlanService = Depends(get_plan_service),
) -> SharedPlanResponse:
    try:
        return service.get_plan(plan_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.post(
    "",
    response_model=SharedPlanResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_plan(
    request: SharedPlanUpsertRequest,
    response: Response,
    service: SharedPlanService = Depends(get_plan_service),
) -> SharedPlanResponse:
    created = service.create_plan(request)
    response.headers["Location"] = f"/api/shared/plans/{created.id}"
    return created


@router.put(
    "/{plan_id}",
    response_model=SharedPlanResponse,
    response_model_by_alias=True,
)
def update_plan(
    plan_id: str,
    request: SharedPlanUpsertRequest,
    service: SharedPlanService = Depends(get_plan_service),
) -> SharedPlanResponse:
    try:
        return service.update_plan(plan_id, request)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: str,
    service: SharedPlanService = Depends(get_plan_service),
) -> Response:
    try:
        service.delete_plan(plan_id)
    except NotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
