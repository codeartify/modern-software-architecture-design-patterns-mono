import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime
from uuid import UUID

from workshop_api.fitness.clean_architecture.entity.membership import Membership
from workshop_api.fitness.clean_architecture.entity.membership_invoice_details import (
    MembershipInvoiceDetails,
)


@dataclass(frozen=True)
class MembershipBillingReference:
    id: UUID
    membership_id: UUID
    external_invoice_id: str
    external_invoice_reference: str
    due_date: date
    status: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        membership: Membership,
        external_invoice_id: str,
        membership_invoice_details: MembershipInvoiceDetails,
    ) -> MembershipBillingReference:
        now = datetime.now(UTC)
        return MembershipBillingReference(
            id=uuid.uuid4(),
            membership_id=membership.id,
            external_invoice_id=external_invoice_id,
            external_invoice_reference=str(membership_invoice_details.membership_id),
            due_date=membership_invoice_details.due_date,
            status="OPEN",
            created_at=now,
            updated_at=now,
        )
