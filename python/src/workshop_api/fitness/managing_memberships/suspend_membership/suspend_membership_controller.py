from datetime import UTC, datetime

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session

from ..shared.membership_entity import (
    MembershipBillingReferenceOrmModel,
    MembershipOrmModel,
)
from .suspend_overdue_memberships_request import (
    SuspendOverdueMembershipsRequest,
)
from .suspend_overdue_memberships_response import (
    SuspendOverdueMembershipsResponse,
)

router = APIRouter(prefix="/api/memberships", tags=["membership"])


@router.post(
    "/suspend-overdue",
    response_model=SuspendOverdueMembershipsResponse,
    response_model_by_alias=True,
)
def suspend_overdue_memberships(
    request: SuspendOverdueMembershipsRequest | None = Body(default=None),
    session: Session = Depends(get_db_session),
) -> SuspendOverdueMembershipsResponse:
    checked_at = request.checked_at if request and request.checked_at else datetime.now(UTC)
    checked_at_date = checked_at.astimezone(UTC).date() if checked_at.tzinfo else checked_at.date()

    memberships = session.query(MembershipOrmModel).all()
    open_billing_references = (
        session.query(MembershipBillingReferenceOrmModel)
        .filter(MembershipBillingReferenceOrmModel.status == "OPEN")
        .all()
    )

    suspended_membership_ids = []
    checked_memberships = 0
    for membership in memberships:
        if not membership.is_active():
            continue

        checked_memberships += 1
        overdue_billing_reference = next(
            (
                billing_reference
                for billing_reference in open_billing_references
                if billing_reference.membership_id == membership.id
                and billing_reference.due_date < checked_at_date
            ),
            None,
        )
        if overdue_billing_reference is None:
            continue

        if not membership.is_suspended_for_non_payment():
            membership.suspend_for_non_payment()
            suspended_membership_ids.append(membership.id)

    session.commit()

    return SuspendOverdueMembershipsResponse(
        checkedAt=checked_at,
        checkedMemberships=checked_memberships,
        suspendedMembershipIds=suspended_membership_ids,
    )
