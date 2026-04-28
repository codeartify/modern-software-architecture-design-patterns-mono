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

from workshop_api.fitness.customer.database import get_db_session
from workshop_api.fitness.customer.models import CustomerOrmModel
from workshop_api.fitness.email.service import email_service
from workshop_api.fitness.external_invoice_provider.models import ExternalInvoiceProviderStatus
from workshop_api.fitness.external_invoice_provider.schemas import (
    ExternalInvoiceProviderResponse,
    ExternalInvoiceProviderUpsertRequest,
)
from workshop_api.fitness.membership.exercise00_mixed.models import (
    E00MembershipBillingReferenceOrmModel,
    E00MembershipOrmModel,
)
from workshop_api.fitness.membership.exercise00_mixed.schemas import (
    E00ActivateMembershipRequest,
    E00ActivateMembershipResponse,
    E00MembershipResponse,
    E00PaymentReceivedRequest,
    E00PaymentReceivedResponse,
    E00SuspendOverdueMembershipsRequest,
    E00SuspendOverdueMembershipsResponse,
)
from workshop_api.fitness.plan.models import PlanOrmModel

router = APIRouter(prefix="/api/e00/memberships", tags=["membership-e00"])


def get_external_invoice_provider_base_url() -> str:
    return os.getenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://127.0.0.1:9090")


def get_billing_sender_email_address() -> str:
    return os.getenv("WORKSHOP_BILLING_SENDER_EMAIL_ADDRESS", "billing@codeartify.com")


def _response_content(response_model: E00PaymentReceivedResponse) -> dict[str, object]:
    if hasattr(response_model, "model_dump"):
        return response_model.model_dump(by_alias=True, mode="json")
    return json.loads(response_model.json(by_alias=True))


@router.get("", response_model=list[E00MembershipResponse], response_model_by_alias=True)
async def list_memberships(
    session: Session = Depends(get_db_session),
) -> list[E00MembershipResponse]:
    memberships = session.query(E00MembershipOrmModel).all()
    return [
        E00MembershipResponse(
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
    response_model=E00MembershipResponse,
    response_model_by_alias=True,
)
async def get_membership(
    membership_id: str,
    session: Session = Depends(get_db_session),
) -> E00MembershipResponse:
    membership = session.get(E00MembershipOrmModel, membership_id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {membership_id} was not found",
        )

    return E00MembershipResponse(
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


@router.post(
    "/activate",
    response_model=E00ActivateMembershipResponse,
    response_model_by_alias=True,
)
async def activate_membership(
    activation_request: E00ActivateMembershipRequest,
    request: Request,
    session: Session = Depends(get_db_session),
    external_invoice_provider_base_url: str = Depends(get_external_invoice_provider_base_url),
    billing_sender_email_address: str = Depends(get_billing_sender_email_address),
) -> E00ActivateMembershipResponse:
    customer = session.get(CustomerOrmModel, activation_request.customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {activation_request.customer_id} was not found",
        )

    plan = session.get(PlanOrmModel, activation_request.plan_id)
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

    membership = E00MembershipOrmModel(
        customer_id=activation_request.customer_id,
        plan_id=activation_request.plan_id,
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

    external_invoice_request = ExternalInvoiceProviderUpsertRequest(
        customerReference=activation_request.customer_id,
        contractReference=membership.id,
        amountInCents=membership.plan_price,
        currency="CHF",
        dueDate=invoice_due_date,
        status=ExternalInvoiceProviderStatus.OPEN,
        description=f"Membership invoice for {plan.title}",
        externalCorrelationId=invoice_id,
        metadata={
            "exercise": "e00",
            "planId": membership.plan_id,
        },
    )

    client_kwargs: dict[str, object] = {"base_url": external_invoice_provider_base_url}
    if external_invoice_provider_base_url.startswith("http://testserver"):
        client_kwargs["transport"] = httpx.ASGITransport(app=request.app)

    async with httpx.AsyncClient(**client_kwargs) as client:
        external_invoice_http_response = await client.post(
            "/api/external-invoice-provider/invoices",
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

    billing_reference = E00MembershipBillingReferenceOrmModel(
        membership_id=membership.id,
        external_invoice_id=(
            external_invoice.invoice_id if external_invoice is not None else invoice_id
        ),
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

    return E00ActivateMembershipResponse(
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
        externalInvoiceId=external_invoice.invoice_id,
        invoiceDueDate=invoice_due_date,
    )


@router.post(
    "/{membership_id}/suspend",
    response_model=E00MembershipResponse,
    response_model_by_alias=True,
)
async def suspend_membership(
    membership_id: str,
    session: Session = Depends(get_db_session),
) -> E00MembershipResponse:
    membership = session.get(E00MembershipOrmModel, membership_id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {membership_id} was not found",
        )

    if membership.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Membership {membership_id} must be ACTIVE to suspend",
        )

    membership.status = "SUSPENDED"
    session.commit()
    session.refresh(membership)

    return E00MembershipResponse(
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


@router.post(
    "/suspend-overdue",
    response_model=E00SuspendOverdueMembershipsResponse,
    response_model_by_alias=True,
)
async def suspend_overdue_memberships(
    suspend_request: E00SuspendOverdueMembershipsRequest | None = None,
    request: Request = None,
    session: Session = Depends(get_db_session),
    external_invoice_provider_base_url: str = Depends(get_external_invoice_provider_base_url),
) -> E00SuspendOverdueMembershipsResponse:
    checked_at = (
        suspend_request.checked_at
        if suspend_request is not None and suspend_request.checked_at is not None
        else datetime.now(UTC)
    )
    checked_at_date = checked_at.date()

    memberships = session.query(E00MembershipOrmModel).all()
    open_billing_references = (
        session.query(E00MembershipBillingReferenceOrmModel)
        .filter(E00MembershipBillingReferenceOrmModel.status == "OPEN")
        .all()
    )

    client_kwargs: dict[str, object] = {"base_url": external_invoice_provider_base_url}
    if external_invoice_provider_base_url.startswith("http://testserver"):
        client_kwargs["transport"] = httpx.ASGITransport(app=request.app)

    try:
        async with httpx.AsyncClient(**client_kwargs) as client:
            external_invoice_http_response = await client.get(
                "/api/external-invoice-provider/invoices"
            )
            external_invoice_http_response.raise_for_status()
            external_invoices = [
                (
                    ExternalInvoiceProviderResponse.model_validate(item)
                    if hasattr(ExternalInvoiceProviderResponse, "model_validate")
                    else ExternalInvoiceProviderResponse.parse_obj(item)
                )
                for item in external_invoice_http_response.json()
            ]
    except httpx.HTTPError:
        external_invoices = []

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

        matching_external_invoice = next(
            (
                invoice
                for invoice in external_invoices
                if invoice.invoice_id == overdue_billing_reference.external_invoice_id
                or invoice.external_correlation_id
                == overdue_billing_reference.external_invoice_reference
                or invoice.contract_reference == membership.id
            ),
            None,
        )

        if (
            matching_external_invoice is not None
            and matching_external_invoice.status != ExternalInvoiceProviderStatus.OPEN
        ):
            continue

        membership.status = "SUSPENDED"
        membership.reason = "NON_PAYMENT"
        suspended_membership_ids.append(membership.id)

    session.commit()

    return E00SuspendOverdueMembershipsResponse(
        checkedAt=checked_at,
        checkedMemberships=checked_memberships,
        suspendedMembershipIds=suspended_membership_ids,
    )


@router.post(
    "/payment-received",
    response_model=E00PaymentReceivedResponse,
    response_model_by_alias=True,
)
async def payment_received(
    payment_request: E00PaymentReceivedRequest,
    session: Session = Depends(get_db_session),
) -> E00PaymentReceivedResponse | JSONResponse:
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
            session.query(E00MembershipBillingReferenceOrmModel)
            .filter(
                E00MembershipBillingReferenceOrmModel.external_invoice_id
                == payment_request.external_invoice_id
            )
            .one_or_none()
        )

    if billing_reference is None and payment_request.external_invoice_reference:
        billing_reference = (
            session.query(E00MembershipBillingReferenceOrmModel)
            .filter(
                E00MembershipBillingReferenceOrmModel.external_invoice_reference
                == payment_request.external_invoice_reference
            )
            .one_or_none()
        )

    if billing_reference is None and payment_request.membership_id:
        billing_reference = (
            session.query(E00MembershipBillingReferenceOrmModel)
            .filter(
                E00MembershipBillingReferenceOrmModel.membership_id
                == payment_request.membership_id
            )
            .first()
        )

    if billing_reference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No billing reference was found",
        )

    paid_at = payment_request.paid_at or datetime.now(UTC)

    if billing_reference.status != "PAID":
        billing_reference.status = "PAID"
        billing_reference.updated_at = paid_at
        session.add(billing_reference)

    membership = session.get(E00MembershipOrmModel, billing_reference.membership_id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {billing_reference.membership_id} was not found",
        )

    previous_membership_status = membership.status
    new_membership_status = membership.status
    message = "Payment recorded"
    reactivated = False

    if membership.status == "ACTIVE":
        message = "Membership remains active"
        session.commit()
        return E00PaymentReceivedResponse(
            paidAt=paid_at,
            membershipId=membership.id,
            billingReferenceId=billing_reference.id,
            previousMembershipStatus=previous_membership_status,
            newMembershipStatus=new_membership_status,
            reactivated=reactivated,
            message=message,
        )

    if membership.status == "SUSPENDED" and membership.reason == "NON_PAYMENT":
        if paid_at.date() <= membership.end_date:
            membership.status = "ACTIVE"
            membership.reason = None
            session.add(membership)
            session.commit()
            session.refresh(membership)
            return E00PaymentReceivedResponse(
                paidAt=paid_at,
                membershipId=membership.id,
                billingReferenceId=billing_reference.id,
                previousMembershipStatus=previous_membership_status,
                newMembershipStatus=membership.status,
                reactivated=True,
                message="Membership reactivated after payment",
            )

        session.commit()
        conflict_response = E00PaymentReceivedResponse(
            paidAt=paid_at,
            membershipId=membership.id,
            billingReferenceId=billing_reference.id,
            previousMembershipStatus=previous_membership_status,
            newMembershipStatus=new_membership_status,
            reactivated=False,
            message="Membership remains suspended because the membership period already ended",
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_response_content(conflict_response),
        )

    if membership.status == "SUSPENDED":
        session.commit()
        conflict_response = E00PaymentReceivedResponse(
            paidAt=paid_at,
            membershipId=membership.id,
            billingReferenceId=billing_reference.id,
            previousMembershipStatus=previous_membership_status,
            newMembershipStatus=new_membership_status,
            reactivated=False,
            message="Membership remains suspended for a different reason",
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_response_content(conflict_response),
        )

    if membership.status == "CANCELLED":
        session.commit()
        conflict_response = E00PaymentReceivedResponse(
            paidAt=paid_at,
            membershipId=membership.id,
            billingReferenceId=billing_reference.id,
            previousMembershipStatus=previous_membership_status,
            newMembershipStatus=new_membership_status,
            reactivated=False,
            message="Membership remains cancelled",
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_response_content(conflict_response),
        )

    if membership.status == "PENDING":
        session.commit()
        conflict_response = E00PaymentReceivedResponse(
            paidAt=paid_at,
            membershipId=membership.id,
            billingReferenceId=billing_reference.id,
            previousMembershipStatus=previous_membership_status,
            newMembershipStatus=new_membership_status,
            reactivated=False,
            message="Pending memberships cannot be activated by payment",
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_response_content(conflict_response),
        )

    session.commit()
    return E00PaymentReceivedResponse(
        paidAt=paid_at,
        membershipId=membership.id,
        billingReferenceId=billing_reference.id,
        previousMembershipStatus=previous_membership_status,
        newMembershipStatus=new_membership_status,
        reactivated=reactivated,
        message=message,
    )
