from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class ActivateMembershipResult:
    membership_id: UUID
    customer_id: UUID
    plan_id: UUID
    plan_price: int
    plan_duration: int
    status: str
    start_date: date
    end_date: date
    invoice_id: UUID
    external_invoice_id: str | None
    invoice_due_date: date
