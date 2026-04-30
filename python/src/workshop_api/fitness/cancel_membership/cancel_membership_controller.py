from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from workshop_api.fitness.cancel_membership.cancel_membership_request import (
    CancelMembershipRequest,
)
from workshop_api.fitness.cancel_membership.cancel_membership_response import (
    CancelMembershipResponse,
)
from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.shared.membership_entity import MembershipOrmModel

router = APIRouter(prefix="/api/memberships", tags=["membership"])


@router.post(
    "/{membership_id}/cancel",
    response_model=CancelMembershipResponse,
    response_model_by_alias=True,
)
def cancel_membership(
    membership_id: UUID,
    request: CancelMembershipRequest | None = Body(default=None),
    session: Session = Depends(get_db_session),
) -> CancelMembershipResponse:
    membership = session.get(MembershipOrmModel, str(membership_id))
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {membership_id} was not found",
        )
    if membership.is_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Membership is already cancelled",
        )

    cancelled_at = request.cancelled_at if request and request.cancelled_at else datetime.now(UTC)
    reason = request.reason if request else None
    previous_status = membership.status

    membership.cancel(cancelled_at, reason)
    session.commit()
    session.refresh(membership)

    return CancelMembershipResponse(
        membershipId=membership.id,
        previousStatus=previous_status,
        newStatus=membership.status,
        cancelledAt=membership.cancelled_at,
        reason=membership.cancellation_reason,
        message="Membership cancelled",
    )
