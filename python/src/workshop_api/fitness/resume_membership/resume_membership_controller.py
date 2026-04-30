from datetime import UTC, date, datetime
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.resume_membership.resume_membership_request import (
    ResumeMembershipRequest,
)
from workshop_api.fitness.resume_membership.resume_membership_response import (
    ResumeMembershipResponse,
)
from workshop_api.fitness.shared.membership_entity import MembershipOrmModel

router = APIRouter(prefix="/api/memberships", tags=["membership"])


@router.post(
    "/{membership_id}/resume",
    response_model=ResumeMembershipResponse,
    response_model_by_alias=True,
)
def resume_membership(
    membership_id: UUID,
    request: ResumeMembershipRequest | None = Body(default=None),
    session: Session = Depends(get_db_session),
) -> ResumeMembershipResponse:
    membership = session.get(MembershipOrmModel, str(membership_id))
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {membership_id} was not found",
        )
    if not membership.is_paused():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only paused memberships can be resumed",
        )
    if membership.end_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expired memberships cannot be resumed",
        )

    resumed_at = request.resumed_at if request and request.resumed_at else datetime.now(UTC)
    reason = request.reason if request else None
    previous_status = membership.status
    previous_pause_start_date = membership.pause_start_date
    previous_pause_end_date = membership.pause_end_date

    membership.resume_after_pause()
    session.commit()
    session.refresh(membership)

    return ResumeMembershipResponse(
        membershipId=membership.id,
        previousStatus=previous_status,
        newStatus=membership.status,
        resumedAt=resumed_at,
        previousPauseStartDate=previous_pause_start_date,
        previousPauseEndDate=previous_pause_end_date,
        endDate=membership.end_date,
        reason=reason,
        message="Membership resumed",
    )
