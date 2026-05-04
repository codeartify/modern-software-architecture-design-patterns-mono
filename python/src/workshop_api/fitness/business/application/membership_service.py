import calendar
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from workshop_api.fitness.business.application.activate_membership_input import (
    ActivateMembershipInput,
)
from workshop_api.fitness.business.application.activate_membership_result import (
    ActivateMembershipResult,
)
from workshop_api.fitness.business.application.customer_too_young_exception import (
    CustomerTooYoungException,
)
from workshop_api.fitness.business.domain.customer_activate_membership_email import (
    CustomerActivateMembershipEmail,
)
from workshop_api.fitness.infrastructure.customer_entity import CustomerOrmModel
from workshop_api.fitness.infrastructure.customer_not_found_exception import (
    CustomerNotFoundException,
)
from workshop_api.fitness.infrastructure.customer_repository import CustomerRepository
from workshop_api.fitness.infrastructure.external_invoice_provider_client import (
    ExternalInvoiceProviderClient,
)
from workshop_api.fitness.infrastructure.in_memory_email_service import InMemoryEmailService
from workshop_api.fitness.infrastructure.membership_billing_reference_repository import (
    MembershipBillingReferenceRepository,
)
from workshop_api.fitness.infrastructure.membership_entity import (
    MembershipBillingReferenceOrmModel,
    MembershipOrmModel,
)
from workshop_api.fitness.infrastructure.membership_repository import MembershipRepository
from workshop_api.fitness.infrastructure.plan_not_found_exception import PlanNotFoundException
from workshop_api.fitness.infrastructure.plan_repository import PlanRepository


class MembershipService:
    def __init__(
        self,
        membership_repository: MembershipRepository,
        customer_repository: CustomerRepository,
        plan_repository: PlanRepository,
        billing_reference_repository: MembershipBillingReferenceRepository,
        email_service: InMemoryEmailService,
        billing_sender_email_address: str,
        external_invoice_provider_client: ExternalInvoiceProviderClient,
    ) -> None:
        self.membership_repository = membership_repository
        self.customer_repository = customer_repository
        self.plan_repository = plan_repository
        self.billing_reference_repository = billing_reference_repository
        self.email_service = email_service
        self.billing_sender_email_address = billing_sender_email_address
        self.external_invoice_provider_client = external_invoice_provider_client

    async def activate_membership(
        self,
        input_data: ActivateMembershipInput,
    ) -> ActivateMembershipResult:
        customer = self.customer_repository.find_by_id(input_data.customer_id)
        if customer is None:
            raise CustomerNotFoundException(
                f"Customer {input_data.customer_id} was not found"
            )

        plan = self.plan_repository.find_by_id(input_data.plan_id)
        if plan is None:
            raise PlanNotFoundException(f"Plan {input_data.plan_id} was not found")

        start_date = date.today()
        end_date = self._plus_months(start_date, plan.duration_in_months)
        customer_age = self._age_on(customer.date_of_birth, start_date)

        if customer_age < 18 and input_data.signed_by_custodian is not True:
            raise CustomerTooYoungException(
                "Customers younger than 18 require signedByCustodian=true"
            )

        membership = MembershipOrmModel(
            customer_id=str(input_data.customer_id),
            plan_id=str(input_data.plan_id),
            plan_price=int(Decimal(plan.price)),
            plan_duration=plan.duration_in_months,
            status="ACTIVE",
            start_date=start_date,
            end_date=end_date,
        )
        membership = self.membership_repository.save(membership)

        invoice_id = str(uuid.uuid4())
        invoice_due_date = date.today() + timedelta(days=30)
        external_invoice_id = await self.external_invoice_provider_client.create_membership_invoice(
            str(input_data.customer_id),
            membership,
            plan,
            invoice_due_date,
            invoice_id,
        )

        now = datetime.now(UTC)
        billing_reference = MembershipBillingReferenceOrmModel(
            membership_id=membership.id,
            external_invoice_id=external_invoice_id,
            external_invoice_reference=invoice_id,
            due_date=invoice_due_date,
            status="OPEN",
            created_at=now,
            updated_at=now,
        )
        billing_reference = self.billing_reference_repository.save(billing_reference)

        self._send_email(self._to_email(billing_reference, customer, membership))

        return ActivateMembershipResult(
            membership_id=uuid.UUID(str(billing_reference.membership_id)),
            customer_id=uuid.UUID(str(membership.customer_id)),
            plan_id=uuid.UUID(str(membership.plan_id)),
            plan_price=membership.plan_price,
            plan_duration=membership.plan_duration,
            status=membership.status,
            start_date=membership.start_date,
            end_date=membership.end_date,
            invoice_id=uuid.UUID(billing_reference.external_invoice_reference),
            external_invoice_id=billing_reference.external_invoice_id,
            invoice_due_date=billing_reference.due_date,
        )

    @staticmethod
    def _age_on(date_of_birth: date, checked_at: date) -> int:
        return checked_at.year - date_of_birth.year - (
            (checked_at.month, checked_at.day) < (date_of_birth.month, date_of_birth.day)
        )

    @staticmethod
    def _plus_months(start_date: date, months: int) -> date:
        total_month_index = start_date.month - 1 + months
        end_year = start_date.year + (total_month_index // 12)
        end_month = (total_month_index % 12) + 1
        end_day = min(start_date.day, calendar.monthrange(end_year, end_month)[1])
        return date(end_year, end_month, end_day)

    @staticmethod
    def _to_email(
        billing_reference: MembershipBillingReferenceOrmModel,
        customer: CustomerOrmModel,
        membership: MembershipOrmModel,
    ) -> CustomerActivateMembershipEmail:
        return CustomerActivateMembershipEmail(
            invoice_id=billing_reference.external_invoice_reference,
            invoice_due_date=billing_reference.due_date,
            email_address=customer.email_address,
            plan_price=membership.plan_price,
            email_template="""
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
""",
        )

    def _send_email(self, email_details: CustomerActivateMembershipEmail) -> None:
        activation_email = email_details.email_template.strip().format(
            to=email_details.email_address,
            sender=self.billing_sender_email_address,
            invoice_id=email_details.invoice_id,
            amount=email_details.plan_price,
            due_date=email_details.invoice_due_date,
        )

        print(activation_email)
        self.email_service.send(activation_email)
