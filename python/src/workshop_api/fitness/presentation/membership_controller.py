import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from workshop_api.fitness.business.application.activate_membership_input import (
    ActivateMembershipInput,
)
from workshop_api.fitness.business.application.customer_too_young_exception import (
    CustomerTooYoungException,
)
from workshop_api.fitness.business.application.membership_service import MembershipService
from workshop_api.fitness.infrastructure.customer_not_found_exception import (
    CustomerNotFoundException,
)
from workshop_api.fitness.infrastructure.customer_repository import CustomerRepository
from workshop_api.fitness.infrastructure.database import get_db_session
from workshop_api.fitness.infrastructure.external_invoice_provider_client import (
    ExternalInvoiceProviderClient,
)
from workshop_api.fitness.infrastructure.in_memory_email_service import email_service
from workshop_api.fitness.infrastructure.membership_billing_reference_repository import (
    MembershipBillingReferenceRepository,
)
from workshop_api.fitness.infrastructure.membership_repository import MembershipRepository
from workshop_api.fitness.infrastructure.plan_not_found_exception import PlanNotFoundException
from workshop_api.fitness.infrastructure.plan_repository import PlanRepository
from workshop_api.fitness.presentation.membership_schemas import (
    ActivateMembershipRequest,
    ActivateMembershipResponse,
    MembershipResponse,
)

router = APIRouter(prefix="/api/memberships", tags=["membership"])


def get_external_invoice_provider_base_url() -> str:
    return os.getenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://127.0.0.1:9090")


def get_billing_sender_email_address() -> str:
    return os.getenv("WORKSHOP_BILLING_SENDER_EMAIL_ADDRESS", "billing@codeartify.com")


def get_membership_service(
    request: Request,
    session: Session = Depends(get_db_session),
    external_invoice_provider_base_url: str = Depends(get_external_invoice_provider_base_url),
    billing_sender_email_address: str = Depends(get_billing_sender_email_address),
) -> MembershipService:
    return MembershipService(
        membership_repository=MembershipRepository(session),
        customer_repository=CustomerRepository(session),
        plan_repository=PlanRepository(session),
        billing_reference_repository=MembershipBillingReferenceRepository(session),
        email_service=email_service,
        billing_sender_email_address=billing_sender_email_address,
        external_invoice_provider_client=ExternalInvoiceProviderClient(
            external_invoice_provider_base_url,
            app=request.app,
        ),
    )


@router.get("", response_model=list[MembershipResponse], response_model_by_alias=True)
async def list_memberships(
    session: Session = Depends(get_db_session),
) -> list[MembershipResponse]:
    memberships = MembershipRepository(session).find_all()
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
    membership = MembershipRepository(session).find_by_id(membership_id)
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
        reason=membership.reason,
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
    service: MembershipService = Depends(get_membership_service),
) -> ActivateMembershipResponse:
    input_data = ActivateMembershipInput(
        activation_request.customer_id,
        activation_request.plan_id,
        activation_request.signed_by_custodian,
    )

    try:
        result = await service.activate_membership(input_data)
    except (CustomerNotFoundException, PlanNotFoundException) as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except CustomerTooYoungException as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    return ActivateMembershipResponse(
        membershipId=result.membership_id,
        customerId=result.customer_id,
        planId=result.plan_id,
        planPrice=result.plan_price,
        planDuration=result.plan_duration,
        status=result.status,
        startDate=result.start_date,
        endDate=result.end_date,
        invoiceId=result.invoice_id,
        externalInvoiceId=result.external_invoice_id,
        invoiceDueDate=result.invoice_due_date,
    )
