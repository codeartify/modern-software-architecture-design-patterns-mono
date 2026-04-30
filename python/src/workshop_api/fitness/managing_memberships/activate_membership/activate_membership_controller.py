import calendar
import json
import os
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.managing_customers.shared.customer_entity import CustomerOrmModel
from workshop_api.fitness.managing_plans.shared.plan_entity import PlanOrmModel

from ..shared.external_invoice_provider_response import (
    ExternalInvoiceProviderResponse,
)
from ..shared.external_invoice_provider_upsert_request import (
    ExternalInvoiceProviderUpsertRequest,
)
from ..shared.in_memory_email_service import email_service
from ..shared.invoice_provider_status import (
    ExternalInvoiceProviderStatus,
)
from ..shared.membership_entity import (
    MembershipBillingReferenceOrmModel,
    MembershipOrmModel,
)
from .activate_membership_request import (
    ActivateMembershipRequest,
)
from .activate_membership_response import (
    ActivateMembershipResponse,
)

router = APIRouter(prefix="/api/memberships", tags=["membership"])


def get_external_invoice_provider_base_url() -> str:
    return os.getenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://127.0.0.1:9090")


def get_billing_sender_email_address() -> str:
    return os.getenv("WORKSHOP_BILLING_SENDER_EMAIL_ADDRESS", "billing@codeartify.com")


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
        id=str(uuid4()),
        customer_id=str(activation_request.customer_id),
        plan_id=str(activation_request.plan_id),
        plan_price=int(Decimal(plan.price)),
        plan_duration=plan.duration_in_months,
        status="ACTIVE",
        reason=None,
        start_date=start_date,
        end_date=end_date,
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)

    invoice_id = str(uuid4())
    invoice_due_date = date.today() + timedelta(days=30)
    now = datetime.now(UTC)

    external_invoice_request = ExternalInvoiceProviderUpsertRequest(
        customerReference=str(activation_request.customer_id),
        contractReference=membership.id,
        amountInCents=membership.plan_price,
        currency="CHF",
        dueDate=invoice_due_date,
        status=ExternalInvoiceProviderStatus.OPEN,
        description=f"Membership invoice for {plan.title}",
        externalCorrelationId=invoice_id,
        metadata={"exercise": "membership", "planId": membership.plan_id},
    )

    external_invoice = await _create_external_invoice(
        request,
        external_invoice_provider_base_url,
        external_invoice_request,
    )
    external_invoice_id = external_invoice.invoice_id if external_invoice else invoice_id

    billing_reference = MembershipBillingReferenceOrmModel(
        id=str(uuid4()),
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
        membershipId=billing_reference.membership_id,
        customerId=membership.customer_id,
        planId=membership.plan_id,
        planPrice=membership.plan_price,
        planDuration=membership.plan_duration,
        status=membership.status,
        startDate=membership.start_date,
        endDate=membership.end_date,
        invoiceId=billing_reference.external_invoice_reference,
        externalInvoiceId=billing_reference.external_invoice_id,
        invoiceDueDate=billing_reference.due_date,
    )


async def _create_external_invoice(
    request: Request,
    external_invoice_provider_base_url: str,
    external_invoice_request: ExternalInvoiceProviderUpsertRequest,
) -> ExternalInvoiceProviderResponse | None:
    client_kwargs: dict[str, object] = {"base_url": external_invoice_provider_base_url}
    if external_invoice_provider_base_url.startswith("http://testserver"):
        client_kwargs["transport"] = httpx.ASGITransport(app=request.app)

    async with httpx.AsyncClient(**client_kwargs) as client:
        external_invoice_http_response = await client.post(
            "/api/shared/external-invoice-provider/invoices",
            json=json.loads(external_invoice_request.model_dump_json(by_alias=True)),
        )
        external_invoice_http_response.raise_for_status()
        return ExternalInvoiceProviderResponse.model_validate(
            external_invoice_http_response.json()
        )
