import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from workshop_api.fitness.hexagon.inside.customer_too_young_exception import (
    CustomerTooYoungException,
)
from workshop_api.fitness.hexagon.inside.membership_service import MembershipService
from workshop_api.fitness.hexagon.inside.port.inbound.activate_membership import (
    ForActivatingMemberships,
)
from workshop_api.fitness.hexagon.inside.port.inbound.activate_membership_input import (
    ActivateMembershipInput,
)
from workshop_api.fitness.hexagon.inside.port.outbound.customer_not_found_exception import (
    CustomerNotFoundException,
)
from workshop_api.fitness.hexagon.inside.port.outbound.plan_not_found_exception import (
    PlanNotFoundException,
)
from workshop_api.fitness.hexagon.outside.driven.mail.in_memory_mail_sender import (
    InMemoryMailSender,
)
from workshop_api.fitness.hexagon.outside.driven.repository.external import (
    ExternalInvoiceRepository,
)
from workshop_api.fitness.hexagon.outside.driven.repository.sqlalchemy import (
    SqlAlchemyCustomerRepository,
    SqlAlchemyMembershipBillingReferencesRepository,
    SqlAlchemyMembershipRepository,
    SqlAlchemyPlanRepository,
)
from workshop_api.fitness.hexagon.outside.driver.activate_membership_request import (
    ActivateMembershipRequest,
)
from workshop_api.fitness.hexagon.outside.driver.activate_membership_response import (
    ActivateMembershipResponse,
)
from workshop_api.fitness.hexagon.outside.driver.membership_response import (
    MembershipResponse,
)
from workshop_api.fitness.layered.infrastructure.customer_repository import CustomerRepository
from workshop_api.fitness.layered.infrastructure.database import get_db_session
from workshop_api.fitness.layered.infrastructure.in_memory_email_service import email_service
from workshop_api.fitness.layered.infrastructure.membership_billing_reference_repository import (
    MembershipBillingReferenceRepository,
)
from workshop_api.fitness.layered.infrastructure.membership_entity import MembershipOrmModel
from workshop_api.fitness.layered.infrastructure.membership_repository import (
    MembershipRepository,
)
from workshop_api.fitness.layered.infrastructure.plan_repository import PlanRepository

router = APIRouter(prefix="/api/memberships", tags=["membership"])


def get_external_invoice_provider_base_url() -> str:
    return os.getenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://127.0.0.1:9090")


def get_billing_sender_email_address() -> str:
    return os.getenv("WORKSHOP_BILLING_SENDER_EMAIL_ADDRESS", "billing@codeartify.com")


def get_activate_membership(
    request: Request,
    session: Session = Depends(get_db_session),
    external_invoice_provider_base_url: str = Depends(get_external_invoice_provider_base_url),
    billing_sender_email_address: str = Depends(get_billing_sender_email_address),
) -> ForActivatingMemberships:
    return MembershipService(
        for_finding_customers=SqlAlchemyCustomerRepository(CustomerRepository(session)),
        for_finding_plans=SqlAlchemyPlanRepository(PlanRepository(session)),
        for_storing_memberships=SqlAlchemyMembershipRepository(MembershipRepository(session)),
        for_creating_invoices=ExternalInvoiceRepository(
            external_invoice_provider_base_url,
            app=request.app,
        ),
        for_storing_billing_references=SqlAlchemyMembershipBillingReferencesRepository(
            MembershipBillingReferenceRepository(session)
        ),
        for_sending_emails=InMemoryMailSender(
            email_service,
            billing_sender_email_address,
        ),
    )


@router.get("", response_model=list[MembershipResponse], response_model_by_alias=True)
async def list_memberships(
    session: Session = Depends(get_db_session),
) -> list[MembershipResponse]:
    return [from_entity(membership) for membership in MembershipRepository(session).find_all()]


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

    return from_entity(membership)


@router.post(
    "/activate",
    response_model=ActivateMembershipResponse,
    response_model_by_alias=True,
)
async def activate_membership(
    activation_request: ActivateMembershipRequest,
    for_activating_memberships: ForActivatingMemberships = Depends(get_activate_membership),
) -> ActivateMembershipResponse:
    input_data = ActivateMembershipInput(
        activation_request.customer_id,
        activation_request.plan_id,
        activation_request.signed_by_custodian,
    )

    try:
        result = await for_activating_memberships.activate_membership(input_data)
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


def from_entity(entity: MembershipOrmModel) -> MembershipResponse:
    return MembershipResponse(
        membershipId=entity.id,
        customerId=entity.customer_id,
        planId=entity.plan_id,
        planPrice=entity.plan_price,
        planDuration=entity.plan_duration,
        status=entity.status,
        reason=entity.reason,
        startDate=entity.start_date,
        endDate=entity.end_date,
    )
