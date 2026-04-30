from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.managing_memberships.pause_membership.pause_membership_request import (
    PauseMembershipRequest,
)
from workshop_api.fitness.managing_memberships.pause_membership.pause_membership_response import (
    PauseMembershipResponse,
)
from workshop_api.fitness.managing_memberships.shared.membership_entity import MembershipOrmModel

router = APIRouter(prefix="/api/memberships", tags=["membership"])


@router.post(
    "/{membership_id}/pause",
    response_model=PauseMembershipResponse,
    response_model_by_alias=True,
)
def pause_membership(
    membership_id: UUID,
    request: PauseMembershipRequest,
    session: Session = Depends(get_db_session),
) -> PauseMembershipResponse:
    if request.pause_start_date is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="pauseStartDate is required",
        )
    if request.pause_end_date is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="pauseEndDate is required",
        )
    if request.pause_end_date < request.pause_start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="pauseEndDate must not be before pauseStartDate",
        )

    membership = session.get(MembershipOrmModel, str(membership_id))
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {membership_id} was not found",
        )
    if not membership.is_active():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active memberships can be paused",
        )
    if membership.end_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expired memberships cannot be paused",
        )

    previous_status = membership.status
    previous_end_date = membership.end_date
    membership.pause(request.pause_start_date, request.pause_end_date, request.reason)
    session.commit()
    session.refresh(membership)

    return PauseMembershipResponse(
        membershipId=membership.id,
        previousStatus=previous_status,
        newStatus=membership.status,
        pauseStartDate=membership.pause_start_date,
        pauseEndDate=membership.pause_end_date,
        previousEndDate=previous_end_date,
        newEndDate=membership.end_date,
        reason=membership.pause_reason,
        message="Membership paused",
    )
