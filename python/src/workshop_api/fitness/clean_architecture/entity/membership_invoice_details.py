import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from workshop_api.fitness.clean_architecture.entity.membership import Membership
from workshop_api.fitness.clean_architecture.entity.plan import Plan


@dataclass(frozen=True)
class MembershipInvoiceDetails:
    id: UUID
    customer_id: UUID
    membership_id: UUID
    plan_id: UUID
    due_date: date
    plan_title: str
    plan_price: Decimal

    INVOICE_DUE_DAYS = 30

    @staticmethod
    def create(
        customer_id: UUID,
        membership: Membership,
        plan: Plan,
    ) -> MembershipInvoiceDetails:
        return MembershipInvoiceDetails(
            id=uuid.uuid4(),
            customer_id=customer_id,
            membership_id=membership.id,
            plan_id=plan.id,
            due_date=date.today() + timedelta(days=MembershipInvoiceDetails.INVOICE_DUE_DAYS),
            plan_title=plan.title,
            plan_price=plan.price,
        )
