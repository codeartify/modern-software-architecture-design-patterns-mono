from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class MembershipInvoiceDetails:
    id: UUID
    customer_id: UUID
    membership_id: UUID
    plan_id: UUID
    due_date: date
    plan_title: str
    plan_price: Decimal
