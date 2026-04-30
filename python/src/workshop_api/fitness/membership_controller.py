import calendar
import json
import os
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from workshop_api.fitness.customer_entity import CustomerOrmModel
from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.in_memory_email_service import email_service
from workshop_api.fitness.invoice_provider_schemas import (
    ExternalInvoiceProviderResponse,
    ExternalInvoiceProviderUpsertRequest,
)
from workshop_api.fitness.invoice_provider_status import ExternalInvoiceProviderStatus
from workshop_api.fitness.membership_entity import (
    MembershipBillingReferenceOrmModel,
    MembershipOrmModel,
)
from workshop_api.fitness.membership_schemas import (
    ActivateMembershipRequest,
    ActivateMembershipResponse,
    CancelMembershipRequest,
    CancelMembershipResponse,
    ExtendMembershipRequest,
    ExtendMembershipResponse,
    MembershipResponse,
    PauseMembershipRequest,
    PauseMembershipResponse,
    PaymentReceivedRequest,
    PaymentReceivedResponse,
    ResumeMembershipRequest,
    ResumeMembershipResponse,
    SuspendOverdueMembershipsRequest,
    SuspendOverdueMembershipsResponse,
)
from workshop_api.fitness.plan_entity import PlanOrmModel

router = APIRouter(prefix="/api/memberships", tags=["membership"])


def get_external_invoice_provider_base_url() -> str:
    return os.getenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://127.0.0.1:9090")


def get_billing_sender_email_address() -> str:
    return os.getenv("WORKSHOP_BILLING_SENDER_EMAIL_ADDRESS", "billing@codeartify.com")


def _response_content(response_model: PaymentReceivedResponse) -> dict[str, object]:
    if hasattr(response_model, "model_dump"):
        return response_model.model_dump(by_alias=True, mode="json")
    return json.loads(response_model.json(by_alias=True))


def _add_months(start_date: date, months: int) -> date:
    total_month_index = start_date.month - 1 + months
    end_year = start_date.year + (total_month_index // 12)
    end_month = (total_month_index % 12) + 1
    end_day = min(start_date.day, calendar.monthrange(end_year, end_month)[1])
    return date(end_year, end_month, end_day)


@router.get("", response_model=list[MembershipResponse], response_model_by_alias=True)
async def list_memberships(
    session: Session = Depends(get_db_session),
) -> list[MembershipResponse]:
    memberships = session.query(MembershipOrmModel).all()
    return [
        MembershipResponse(
            membershipId=membership.id,
            customerId=membership.customer_id,
            planId=membership.plan_id,
            planPrice=membership.plan_price,
            planDuration=membership.plan_duration,
            status=membership.status,
            reason=membership.reason,
            startDate=membership.start_date,
            endDate=membership.end_date,
        )
        for membership in memberships
    ]


@router.get(
    "/{membership_id}",
    response_model=MembershipResponse,
    response_model_by_alias=True,
)
async def get_membership(
    membership_id: uuid.UUID,
    session: Session = Depends(get_db_session),
) -> MembershipResponse:
    membership = session.get(MembershipOrmModel, str(membership_id))
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {membership_id} was not found",
        )

    return MembershipResponse(
        membershipId=membership.id,
        customerId=membership.customer_id,
        planId=membership.plan_id,
        planPrice=membership.plan_price,
        planDuration=membership.plan_duration,
        status=membership.status,
        startDate=membership.start_date,
        endDate=membership.end_date,
    )


@router.post(
    "/activate",
    response_model=ActivateMembershipResponse,
    response_model_by_alias=True,
)
async def activate_membership(
    activation_request: ActivateMembershipRequest,
    request: Request,
    session: Session = Depends(get_db_session),
    external_invoice_provider_base_url: str = Depends(get_external_invoice_provider_base_url),
    billing_sender_email_address: str = Depends(get_billing_sender_email_address),
) -> ActivateMembershipResponse:
    customer = session.get(CustomerOrmModel, str(activation_request.customer_id))
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {activation_request.customer_id} was not found",
        )

    plan = session.get(PlanOrmModel, str(activation_request.plan_id))
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {activation_request.plan_id} was not found",
        )

    start_date = date.today()
    total_month_index = start_date.month - 1 + plan.duration_in_months
    end_year = start_date.year + (total_month_index // 12)
    end_month = (total_month_index % 12) + 1
    end_day = min(start_date.day, calendar.monthrange(end_year, end_month)[1])
    end_date = date(end_year, end_month, end_day)
    customer_age = start_date.year - customer.date_of_birth.year - (
        (start_date.month, start_date.day)
        < (customer.date_of_birth.month, customer.date_of_birth.day)
    )

    if customer_age < 18 and activation_request.signed_by_custodian is not True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customers younger than 18 require signedByCustodian=true",
        )

    membership = MembershipOrmModel(
        customer_id=str(activation_request.customer_id),
        plan_id=str(activation_request.plan_id),
        plan_price=int(Decimal(plan.price)),
        plan_duration=plan.duration_in_months,
        status="ACTIVE",
        start_date=start_date,
        end_date=end_date,
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)

    invoice_id = str(uuid.uuid4())
    invoice_due_date = start_date + timedelta(days=30)
    now = datetime.now(UTC)
    external_invoice_id: str | None

    external_invoice_request = ExternalInvoiceProviderUpsertRequest(
        customerReference=str(activation_request.customer_id),
        contractReference=membership.id,
        amountInCents=membership.plan_price,
        currency="CHF",
        dueDate=invoice_due_date,
        status=ExternalInvoiceProviderStatus.OPEN,
        description=f"Membership invoice for {plan.title}",
        externalCorrelationId=invoice_id,
        metadata={
            "exercise": "membership",
            "planId": membership.plan_id,
        },
    )

    client_kwargs: dict[str, object] = {"base_url": external_invoice_provider_base_url}
    if external_invoice_provider_base_url.startswith("http://testserver"):
        client_kwargs["transport"] = httpx.ASGITransport(app=request.app)

    async with httpx.AsyncClient(**client_kwargs) as client:
        external_invoice_http_response = await client.post(
            "/api/shared/external-invoice-provider/invoices",
            json=json.loads(
                external_invoice_request.model_dump_json(by_alias=True)
                if hasattr(external_invoice_request, "model_dump_json")
                else external_invoice_request.json(by_alias=True)
            ),
        )
        external_invoice_http_response.raise_for_status()
        external_invoice = (
            ExternalInvoiceProviderResponse.model_validate(external_invoice_http_response.json())
            if hasattr(ExternalInvoiceProviderResponse, "model_validate")
            else ExternalInvoiceProviderResponse.parse_obj(external_invoice_http_response.json())
        )

    external_invoice_id = (
        external_invoice.invoice_id if external_invoice is not None else invoice_id
    )

    billing_reference = MembershipBillingReferenceOrmModel(
        membership_id=membership.id,
        external_invoice_id=external_invoice_id,
        external_invoice_reference=invoice_id,
        due_date=invoice_due_date,
        status="OPEN",
        created_at=now,
        updated_at=now,
    )
    session.add(billing_reference)
    session.commit()

    email = """
To: {to}
From: {sender}
Subject: Your Membership Invoice {invoice_id}

Dear customer,

Thank you for your membership.

Please find your invoice details below:
Invoice ID: {invoice_id}
Amount Due: CHF {amount}
Due Date: {due_date}

Attachment: invoice-{invoice_id}.pdf

Kind regards,
Codeartify Billing
""".strip().format(
        to=customer.email_address,
        sender=billing_sender_email_address,
        invoice_id=invoice_id,
        amount=membership.plan_price,
        due_date=invoice_due_date,
    )
    print(email)
    email_service.send(email)

    return ActivateMembershipResponse(
        membershipId=membership.id,
        customerId=membership.customer_id,
        planId=membership.plan_id,
        planPrice=membership.plan_price,
        planDuration=membership.plan_duration,
        status=membership.status,
        reason=membership.reason,
        startDate=membership.start_date,
        endDate=membership.end_date,
        invoiceId=invoice_id,
        externalInvoiceId=external_invoice_id,
        invoiceDueDate=invoice_due_date,
    )


@router.post(
    "/suspend-overdue",
    response_model=SuspendOverdueMembershipsResponse,
    response_model_by_alias=True,
)
async def suspend_overdue_memberships(
    suspend_request: SuspendOverdueMembershipsRequest | None = None,
    session: Session = Depends(get_db_session),
) -> SuspendOverdueMembershipsResponse:
    checked_at = (
        suspend_request.checked_at
        if suspend_request is not None and suspend_request.checked_at is not None
        else datetime.now(UTC)
    )
    checked_at_date = checked_at.date()

    memberships = session.query(MembershipOrmModel).all()
    open_billing_references = (
        session.query(MembershipBillingReferenceOrmModel)
        .filter(MembershipBillingReferenceOrmModel.status == "OPEN")
        .all()
    )

    checked_memberships = 0
    suspended_membership_ids: list[str] = []

    for membership in memberships:
        if membership.status != "ACTIVE":
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

        membership.status = "SUSPENDED"
        membership.reason = "NON_PAYMENT"
        suspended_membership_ids.append(membership.id)

    session.commit()

    return SuspendOverdueMembershipsResponse(
        checkedAt=checked_at,
        checkedMemberships=checked_memberships,
        suspendedMembershipIds=suspended_membership_ids,
    )


@router.post(
    "/{membership_id}/pause",
    response_model=PauseMembershipResponse,
    response_model_by_alias=True,
)
async def pause_membership(
    membership_id: uuid.UUID,
    pause_request: PauseMembershipRequest,
    session: Session = Depends(get_db_session),
) -> PauseMembershipResponse:
    if pause_request.pause_start_date is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="pauseStartDate is required",
        )

    if pause_request.pause_end_date is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="pauseEndDate is required",
        )

    if pause_request.pause_end_date < pause_request.pause_start_date:
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

    if membership.status != "ACTIVE":
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
    pause_days = (pause_request.pause_end_date - pause_request.pause_start_date).days + 1

    membership.status = "PAUSED"
    membership.pause_start_date = pause_request.pause_start_date
    membership.pause_end_date = pause_request.pause_end_date
    membership.pause_reason = pause_request.reason
    membership.end_date = membership.end_date + timedelta(days=pause_days)
    session.add(membership)
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


@router.post(
    "/{membership_id}/resume",
    response_model=ResumeMembershipResponse,
    response_model_by_alias=True,
)
async def resume_membership(
    membership_id: uuid.UUID,
    resume_request: ResumeMembershipRequest | None = None,
    session: Session = Depends(get_db_session),
) -> ResumeMembershipResponse:
    membership = session.get(MembershipOrmModel, str(membership_id))
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {membership_id} was not found",
        )

    if membership.status != "PAUSED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only paused memberships can be resumed",
        )

    if membership.end_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expired memberships cannot be resumed",
        )

    resumed_at = (
        resume_request.resumed_at
        if resume_request is not None and resume_request.resumed_at is not None
        else datetime.now(UTC)
    )
    reason = resume_request.reason if resume_request is not None else None
    previous_status = membership.status
    previous_pause_start_date = membership.pause_start_date
    previous_pause_end_date = membership.pause_end_date

    membership.status = "ACTIVE"
    membership.pause_start_date = None
    membership.pause_end_date = None
    membership.pause_reason = None
    session.add(membership)
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


@router.post(
    "/{membership_id}/cancel",
    response_model=CancelMembershipResponse,
    response_model_by_alias=True,
)
async def cancel_membership(
    membership_id: uuid.UUID,
    cancel_request: CancelMembershipRequest | None = None,
    session: Session = Depends(get_db_session),
) -> CancelMembershipResponse:
    membership = session.get(MembershipOrmModel, str(membership_id))
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {membership_id} was not found",
        )

    if membership.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Membership is already cancelled",
        )

    cancelled_at = (
        cancel_request.cancelled_at
        if cancel_request is not None and cancel_request.cancelled_at is not None
        else datetime.now(UTC)
    )
    reason = cancel_request.reason if cancel_request is not None else None
    previous_status = membership.status

    membership.status = "CANCELLED"
    membership.cancelled_at = cancelled_at
    membership.cancellation_reason = reason
    session.add(membership)
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


@router.post(
    "/{membership_id}/extend",
    response_model=ExtendMembershipResponse,
    response_model_by_alias=True,
)
async def extend_membership(
    membership_id: uuid.UUID,
    extension_request: ExtendMembershipRequest,
    request: Request,
    session: Session = Depends(get_db_session),
    external_invoice_provider_base_url: str = Depends(get_external_invoice_provider_base_url),
) -> ExtendMembershipResponse:
    membership = session.get(MembershipOrmModel, str(membership_id))
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {membership_id} was not found",
        )

    if membership.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelled memberships cannot be extended",
        )

    if membership.end_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expired memberships cannot be extended",
        )

    additional_months = extension_request.additional_months or 0
    additional_days = extension_request.additional_days or 0
    billable = extension_request.billable is True

    if additional_months < 0 or additional_days < 0 or (
        additional_months == 0 and additional_days == 0
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Extension duration must be positive",
        )

    if billable and (extension_request.price is None or extension_request.price <= 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Billable extensions require a positive price",
        )

    previous_end_date = membership.end_date
    membership.end_date = _add_months(membership.end_date, additional_months) + timedelta(
        days=additional_days
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)

    if not billable:
        return ExtendMembershipResponse(
            membershipId=membership.id,
            status=membership.status,
            previousEndDate=previous_end_date,
            newEndDate=membership.end_date,
            billable=False,
            message="Membership extended",
        )

    invoice_id = str(uuid.uuid4())
    invoice_due_date = date.today() + timedelta(days=30)
    now = datetime.now(UTC)

    external_invoice_request = ExternalInvoiceProviderUpsertRequest(
        customerReference=membership.customer_id,
        contractReference=membership.id,
        amountInCents=extension_request.price,
        currency="CHF",
        dueDate=invoice_due_date,
        status=ExternalInvoiceProviderStatus.OPEN,
        description="Membership extension invoice",
        externalCorrelationId=invoice_id,
        metadata={
            "exercise": "membership",
            "membershipId": membership.id,
            "extension": "true",
        },
    )

    client_kwargs: dict[str, object] = {"base_url": external_invoice_provider_base_url}
    if external_invoice_provider_base_url.startswith("http://testserver"):
        client_kwargs["transport"] = httpx.ASGITransport(app=request.app)

    async with httpx.AsyncClient(**client_kwargs) as client:
        external_invoice_http_response = await client.post(
            "/api/shared/external-invoice-provider/invoices",
            json=json.loads(
                external_invoice_request.model_dump_json(by_alias=True)
                if hasattr(external_invoice_request, "model_dump_json")
                else external_invoice_request.json(by_alias=True)
            ),
        )
        external_invoice_http_response.raise_for_status()
        external_invoice = (
            ExternalInvoiceProviderResponse.model_validate(external_invoice_http_response.json())
            if hasattr(ExternalInvoiceProviderResponse, "model_validate")
            else ExternalInvoiceProviderResponse.parse_obj(external_invoice_http_response.json())
        )

    external_invoice_id = (
        external_invoice.invoice_id if external_invoice is not None else invoice_id
    )
    billing_reference = MembershipBillingReferenceOrmModel(
        membership_id=membership.id,
        external_invoice_id=external_invoice_id,
        external_invoice_reference=invoice_id,
        due_date=invoice_due_date,
        status="OPEN",
        created_at=now,
        updated_at=now,
    )
    session.add(billing_reference)
    session.commit()

    return ExtendMembershipResponse(
        membershipId=membership.id,
        status=membership.status,
        previousEndDate=previous_end_date,
        newEndDate=membership.end_date,
        billable=True,
        billingReferenceId=billing_reference.id,
        externalInvoiceReference=billing_reference.external_invoice_reference,
        externalInvoiceId=billing_reference.external_invoice_id,
        invoiceDueDate=billing_reference.due_date,
        message="Membership extended and invoice created",
    )


@router.post(
    "/payment-received",
    response_model=PaymentReceivedResponse,
    response_model_by_alias=True,
)
async def payment_received(
    payment_request: PaymentReceivedRequest,
    session: Session = Depends(get_db_session),
) -> PaymentReceivedResponse | JSONResponse:
    if (
        not payment_request.external_invoice_id
        and not payment_request.external_invoice_reference
        and not payment_request.membership_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one invoice or membership identifier must be provided",
        )

    billing_reference = None
    if payment_request.external_invoice_id:
        billing_reference = (
            session.query(MembershipBillingReferenceOrmModel)
            .filter(
                MembershipBillingReferenceOrmModel.external_invoice_id
                == payment_request.external_invoice_id
            )
            .one_or_none()
        )

    if billing_reference is None and payment_request.external_invoice_reference:
        billing_reference = (
            session.query(MembershipBillingReferenceOrmModel)
            .filter(
                MembershipBillingReferenceOrmModel.external_invoice_reference
                == payment_request.external_invoice_reference
            )
            .one_or_none()
        )

    if billing_reference is None and payment_request.membership_id:
        billing_reference = (
            session.query(MembershipBillingReferenceOrmModel)
            .filter(
                MembershipBillingReferenceOrmModel.membership_id
                == str(payment_request.membership_id)
            )
            .first()
        )

    if billing_reference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No billing reference was found",
        )

    paid_at = payment_request.paid_at or datetime.now(UTC)
    message = (
        "Payment was already recorded; membership status unchanged"
        if billing_reference.status == "PAID"
        else "Payment recorded; membership status unchanged"
    )

    if billing_reference.status != "PAID":
        billing_reference.status = "PAID"
        billing_reference.updated_at = paid_at
        session.add(billing_reference)

    membership = session.get(MembershipOrmModel, billing_reference.membership_id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {billing_reference.membership_id} was not found",
        )

    previous_membership_status = membership.status
    new_membership_status = membership.status
    reactivated = False

    if membership.status == "CANCELLED":
        message = "Payment recorded; membership is cancelled and remains unchanged"
    elif membership.status == "SUSPENDED" and membership.reason == "NON_PAYMENT":
        if paid_at.date() <= membership.end_date:
            membership.status = "ACTIVE"
            membership.reason = None
            session.add(membership)
            new_membership_status = "ACTIVE"
            reactivated = True
            message = "Payment recorded; membership reactivated"

    session.commit()
    if reactivated:
        session.refresh(membership)
        new_membership_status = membership.status

    return PaymentReceivedResponse(
        paidAt=paid_at,
        membershipId=membership.id,
        billingReferenceId=billing_reference.id,
        previousMembershipStatus=previous_membership_status,
        newMembershipStatus=new_membership_status,
        reactivated=reactivated,
        message=message,
    )
