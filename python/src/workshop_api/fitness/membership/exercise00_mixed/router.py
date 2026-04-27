import calendar
import json
import os
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from workshop_api.fitness.customer.database import get_db_session
from workshop_api.fitness.customer.models import CustomerOrmModel
from workshop_api.fitness.email.service import email_service
from workshop_api.fitness.external_invoice_provider.models import ExternalInvoiceProviderStatus
from workshop_api.fitness.external_invoice_provider.schemas import (
    ExternalInvoiceProviderResponse,
    ExternalInvoiceProviderUpsertRequest,
)
from workshop_api.fitness.membership.exercise00_mixed.models import E00MembershipOrmModel
from workshop_api.fitness.membership.exercise00_mixed.schemas import (
    E00ActivateMembershipRequest,
    E00ActivateMembershipResponse,
)
from workshop_api.fitness.plan.models import PlanOrmModel

router = APIRouter(prefix="/api/e00/memberships", tags=["membership-e00"])


@dataclass
class E00Invoice:
    id: str
    membership_id: str
    customer_id: str
    amount: int
    due_date: date


def get_external_invoice_provider_base_url() -> str:
    return os.getenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://127.0.0.1:9090")


def get_billing_sender_email_address() -> str:
    return os.getenv("WORKSHOP_BILLING_SENDER_EMAIL_ADDRESS", "billing@codeartify.com")


@router.post("/activate", response_model=E00ActivateMembershipResponse, response_model_by_alias=True)
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
        (start_date.month, start_date.day) < (customer.date_of_birth.month, customer.date_of_birth.day)
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

    invoice = E00Invoice(
        id=str(uuid.uuid4()),
        membership_id=membership.id,
        customer_id=activation_request.customer_id,
        amount=membership.plan_price,
        due_date=start_date + timedelta(days=30),
    )

    external_invoice_request = ExternalInvoiceProviderUpsertRequest(
        customerReference=invoice.customer_id,
        contractReference=invoice.membership_id,
        amountInCents=invoice.amount,
        currency="CHF",
        dueDate=invoice.due_date,
        status=ExternalInvoiceProviderStatus.OPEN,
        description=f"Membership invoice for {plan.title}",
        externalCorrelationId=invoice.id,
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
        invoice_id=invoice.id,
        amount=invoice.amount,
        due_date=invoice.due_date,
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
        startDate=membership.start_date,
        endDate=membership.end_date,
        invoiceId=invoice.id,
        externalInvoiceId=external_invoice.invoice_id,
        invoiceDueDate=invoice.due_date,
    )
