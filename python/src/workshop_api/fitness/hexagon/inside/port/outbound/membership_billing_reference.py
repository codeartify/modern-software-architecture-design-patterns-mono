from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


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
