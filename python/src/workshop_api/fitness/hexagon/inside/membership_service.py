import calendar
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from workshop_api.fitness.hexagon.inside.customer_too_young_exception import (
    CustomerTooYoungException,
)
from workshop_api.fitness.hexagon.inside.port.inbound.activate_membership import (
    ActivateMembership,
)
from workshop_api.fitness.hexagon.inside.port.inbound.activate_membership_input import (
    ActivateMembershipInput,
)
from workshop_api.fitness.hexagon.inside.port.inbound.activate_membership_result import (
    ActivateMembershipResult,
)
from workshop_api.fitness.hexagon.inside.port.outbound.customer_activate_membership_email import (
    CustomerActivateMembershipEmail,
)
from workshop_api.fitness.hexagon.inside.port.outbound.for_creating_invoices import (
    ForCreatingInvoices,
)
from workshop_api.fitness.hexagon.inside.port.outbound.for_finding_customers import (
    ForFindingCustomers,
)
from workshop_api.fitness.hexagon.inside.port.outbound.for_finding_plans import (
    ForFindingPlans,
)
from workshop_api.fitness.hexagon.inside.port.outbound.for_sending_emails import (
    ForSendingEmails,
)
from workshop_api.fitness.hexagon.inside.port.outbound.for_storing_billing_references import (
    ForStoringBillingReferences,
)
from workshop_api.fitness.hexagon.inside.port.outbound.for_storing_memberships import (
    ForStoringMemberships,
)
from workshop_api.fitness.hexagon.inside.port.outbound.membership import Membership
from workshop_api.fitness.hexagon.inside.port.outbound.membership_billing_reference import (
    MembershipBillingReference,
)
from workshop_api.fitness.hexagon.inside.port.outbound.membership_invoice_details import (
    MembershipInvoiceDetails,
)


class MembershipService(ActivateMembership):
    def __init__(
        self,
        for_finding_customers: ForFindingCustomers,
        for_finding_plans: ForFindingPlans,
        for_storing_memberships: ForStoringMemberships,
        for_creating_invoices: ForCreatingInvoices,
        for_storing_billing_references: ForStoringBillingReferences,
        for_sending_emails: ForSendingEmails,
    ) -> None:
        self.for_finding_customers = for_finding_customers
        self.for_finding_plans = for_finding_plans
        self.for_storing_memberships = for_storing_memberships
        self.for_creating_invoices = for_creating_invoices
        self.for_storing_billing_references = for_storing_billing_references
        self.for_sending_emails = for_sending_emails

    async def activate_membership(
        self,
        input_data: ActivateMembershipInput,
    ) -> ActivateMembershipResult:
        customer_id = uuid.UUID(input_data.customer_id)
        customer = self.for_finding_customers.find_customer_by_id(customer_id)

        plan_id = uuid.UUID(input_data.plan_id)
        plan = self.for_finding_plans.find_plan_by_id(plan_id)

        start_date = date.today()
        end_date = self._plus_months(start_date, plan.duration_in_months)

        if self._age_on(customer.date_of_birth, start_date) < 18 and (
            input_data.signed_by_custodian is not True
        ):
            raise CustomerTooYoungException(
                "Customers younger than 18 require signedByCustodian=true"
            )

        membership = Membership(
            id=uuid.uuid4(),
            customer_id=customer_id,
            plan_id=plan_id,
            plan_price=int(Decimal(plan.price)),
            plan_duration_in_months=plan.duration_in_months,
            status="ACTIVE",
            status_reason=None,
            start_date=start_date,
            end_date=end_date,
        )

        stored_membership = self.for_storing_memberships.store_membership(membership)
        invoice_details = MembershipInvoiceDetails(
            id=uuid.uuid4(),
            customer_id=customer_id,
            membership_id=membership.id,
            plan_id=plan.id,
            due_date=date.today() + timedelta(days=30),
            plan_title=plan.title,
            plan_price=plan.price,
        )

        external_invoice_id = await self.for_creating_invoices.create_invoice_with(
            invoice_details
        )

        now = datetime.now(UTC)
        billing_reference = MembershipBillingReference(
            id=uuid.uuid4(),
            membership_id=stored_membership.id,
            external_invoice_id=external_invoice_id,
            external_invoice_reference=str(invoice_details.membership_id),
            due_date=invoice_details.due_date,
            status="OPEN",
            created_at=now,
            updated_at=now,
        )

        stored_billing_reference = (
            self.for_storing_billing_references.store_membership_billing_reference(
                billing_reference
            )
        )

        self.for_sending_emails.send_email(
            self._to_email(
                stored_billing_reference,
                customer.email_address,
                stored_membership.plan_price,
            )
        )

        return ActivateMembershipResult(
            membership_id=str(stored_billing_reference.membership_id),
            customer_id=str(stored_membership.customer_id),
            plan_id=str(stored_membership.plan_id),
            plan_price=stored_membership.plan_price,
            plan_duration=stored_membership.plan_duration_in_months,
            status=stored_membership.status,
            start_date=stored_membership.start_date,
            end_date=stored_membership.end_date,
            invoice_id=stored_billing_reference.external_invoice_reference,
            external_invoice_id=stored_billing_reference.external_invoice_id,
            invoice_due_date=stored_billing_reference.due_date,
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
        billing_reference: MembershipBillingReference,
        email_address: str,
        membership_plan_price: int,
    ) -> CustomerActivateMembershipEmail:
        return CustomerActivateMembershipEmail(
            invoice_id=billing_reference.external_invoice_reference,
            invoice_due_date=billing_reference.due_date,
            email_address=email_address,
            plan_price=membership_plan_price,
            email_template="""
|To: {to}
|From: {sender}
|Subject: Your Membership Invoice {invoice_id}
|
|Dear customer,
|
|Thank you for your membership.
|
|Please find your invoice details below:
|Invoice ID: {invoice_id}
|Amount Due: CHF {amount}
|Due Date: {due_date}
|
|Attachment: invoice-{invoice_id}.pdf
|
|Kind regards,
|Codeartify Billing
|""",
        )
