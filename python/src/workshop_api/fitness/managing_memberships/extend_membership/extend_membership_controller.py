import json
import os
from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session

from ..shared.external_invoice_provider_response import (
    ExternalInvoiceProviderResponse,
)
from ..shared.external_invoice_provider_upsert_request import (
    ExternalInvoiceProviderUpsertRequest,
)
from ..shared.invoice_provider_status import (
    ExternalInvoiceProviderStatus,
)
from ..shared.membership_entity import (
    MembershipBillingReferenceOrmModel,
    MembershipOrmModel,
)
from .extend_membership_request import (
    ExtendMembershipRequest,
)
from .extend_membership_response import (
    ExtendMembershipResponse,
)

router = APIRouter(prefix="/api/memberships", tags=["membership"])


def get_external_invoice_provider_base_url() -> str:
    return os.getenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://127.0.0.1:9090")


@router.post(
    "/{membership_id}/extend",
    response_model=ExtendMembershipResponse,
    response_model_by_alias=True,
)
async def extend_membership(
    membership_id: UUID,
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

    additional_months = extension_request.additional_months or 0
    additional_days = extension_request.additional_days or 0
    billable = extension_request.billable is True

    if membership.is_cancelled():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelled memberships cannot be extended",
        )
    if membership.end_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expired memberships cannot be extended",
        )
    if (
        additional_months < 0
        or additional_days < 0
        or (additional_months == 0 and additional_days == 0)
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
    membership.extend_by(additional_months, additional_days)
    session.commit()
    session.refresh(membership)

    if not billable:
        return ExtendMembershipResponse(
            membershipId=membership.id,
            status=membership.status,
            previousEndDate=previous_end_date,
            newEndDate=membership.end_date,
            billable=False,
            billingReferenceId=None,
            externalInvoiceReference=None,
            externalInvoiceId=None,
            invoiceDueDate=None,
            message="Membership extended",
        )

    invoice_id = str(uuid4())
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
    session.refresh(billing_reference)

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
