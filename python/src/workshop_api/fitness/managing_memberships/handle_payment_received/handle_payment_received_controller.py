from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session

from ..shared.membership_entity import (
    MembershipBillingReferenceOrmModel,
    MembershipOrmModel,
)
from .payment_received_request import (
    PaymentReceivedRequest,
)
from .payment_received_response import (
    PaymentReceivedResponse,
)

router = APIRouter(prefix="/api/memberships", tags=["membership"])


@router.post(
    "/payment-received",
    response_model=PaymentReceivedResponse,
    response_model_by_alias=True,
)
def payment_received(
    request: PaymentReceivedRequest,
    session: Session = Depends(get_db_session),
) -> PaymentReceivedResponse:
    if (
        _is_blank(request.external_invoice_id)
        and _is_blank(request.external_invoice_reference)
        and _is_blank(request.membership_id)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one invoice or membership identifier must be provided",
        )

    billing_reference = None
    if not _is_blank(request.external_invoice_id):
        billing_reference = (
            session.query(MembershipBillingReferenceOrmModel)
            .filter(
                MembershipBillingReferenceOrmModel.external_invoice_id
                == request.external_invoice_id
            )
            .first()
        )

    if billing_reference is None and not _is_blank(request.external_invoice_reference):
        billing_reference = (
            session.query(MembershipBillingReferenceOrmModel)
            .filter(
                MembershipBillingReferenceOrmModel.external_invoice_reference
                == request.external_invoice_reference
            )
            .first()
        )

    if billing_reference is None and not _is_blank(request.membership_id):
        billing_reference = (
            session.query(MembershipBillingReferenceOrmModel)
            .filter(MembershipBillingReferenceOrmModel.membership_id == request.membership_id)
            .first()
        )

    if billing_reference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No billing reference was found",
        )

    paid_at = request.paid_at if request.paid_at is not None else datetime.now(UTC)
    message = (
        "Payment was already recorded; membership status unchanged"
        if billing_reference.is_paid()
        else "Payment recorded; membership status unchanged"
    )

    if not billing_reference.is_paid():
        billing_reference.mark_paid(paid_at)
        session.commit()
        session.refresh(billing_reference)

    membership = session.get(MembershipOrmModel, billing_reference.membership_id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {billing_reference.membership_id} was not found",
        )

    previous_membership_status = membership.status
    new_membership_status = membership.status
    reactivated = False

    if membership.is_cancelled():
        message = "Payment recorded; membership is cancelled and remains unchanged"
    elif membership.is_suspended_for_non_payment() and _as_utc_date(paid_at) <= membership.end_date:
        membership.reactivate_after_payment()
        session.commit()
        session.refresh(membership)
        new_membership_status = membership.status
        message = "Payment recorded; membership reactivated"
        reactivated = True

    return PaymentReceivedResponse(
        paidAt=paid_at,
        membershipId=membership.id,
        billingReferenceId=billing_reference.id,
        previousMembershipStatus=previous_membership_status,
        newMembershipStatus=new_membership_status,
        reactivated=reactivated,
        message=message,
    )


def _is_blank(value: str | None) -> bool:
    return value is None or value.strip() == ""


def _as_utc_date(value: datetime):
    if value.tzinfo is None:
        return value.date()
    return value.astimezone(UTC).date()
