from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ActivateMembershipResult:
    membership_id: str
    customer_id: str
    plan_id: str
    plan_price: int
    plan_duration: int
    status: str
    start_date: date
    end_date: date
    invoice_id: str
    external_invoice_id: str
    invoice_due_date: date
