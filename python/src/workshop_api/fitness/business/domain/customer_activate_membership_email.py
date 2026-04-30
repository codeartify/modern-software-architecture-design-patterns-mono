from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CustomerActivateMembershipEmail:
    invoice_id: str
    invoice_due_date: date
    email_address: str
    plan_price: int
    email_template: str
