import uuid
from datetime import date

from ..entity import (
    CustomerActivateMembershipEmail,
    Membership,
    MembershipBillingReference,
    MembershipInvoiceDetails,
)
from .port.inbound import (
    ActivateMembershipInput,
    ActivateMembershipResult,
    ActivateMembershipUseCase,
)
from .port.outbound import (
    ForCreatingInvoices,
    ForFindingCustomers,
    ForFindingPlans,
    ForSendingEmails,
    ForStoringBillingReferences,
    ForStoringMemberships,
)


class ActivateMembershipUseCaseInteractor(ActivateMembershipUseCase):
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

        membership = Membership.create(
            customer,
            plan_id,
            input_data.signed_by_custodian,
            date.today(),
            plan.duration_in_months,
            plan.price,
        )

        stored_membership = self.for_storing_memberships.store_membership(membership)
        invoice_details = MembershipInvoiceDetails.create(customer_id, membership, plan)
        external_invoice_id = await self.for_creating_invoices.create_invoice_with(
            invoice_details
        )
        billing_reference = MembershipBillingReference.create(
            stored_membership,
            external_invoice_id,
            invoice_details,
        )
        stored_billing_reference = (
            self.for_storing_billing_references.store_membership_billing_reference(
                billing_reference
            )
        )

        email = CustomerActivateMembershipEmail.to_email(
            stored_billing_reference,
            customer.email_address,
            stored_membership.plan_price,
        )
        self.for_sending_emails.send_email(email)

        return self._to_result(stored_billing_reference, stored_membership)

    @staticmethod
    def _to_result(
        stored_billing_reference: MembershipBillingReference,
        membership: Membership,
    ) -> ActivateMembershipResult:
        return ActivateMembershipResult(
            membership_id=str(stored_billing_reference.membership_id),
            customer_id=str(membership.customer_id),
            plan_id=str(membership.plan_id),
            plan_price=membership.plan_price,
            plan_duration=membership.plan_duration_in_months,
            status=membership.status,
            start_date=membership.start_date,
            end_date=membership.end_date,
            invoice_id=stored_billing_reference.external_invoice_reference,
            external_invoice_id=stored_billing_reference.external_invoice_id,
            invoice_due_date=stored_billing_reference.due_date,
        )
