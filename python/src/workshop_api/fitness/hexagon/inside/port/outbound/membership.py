from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class Membership:
    id: UUID
    customer_id: UUID
    plan_id: UUID
    plan_price: int
    plan_duration_in_months: int
    status: str
    status_reason: str | None
    start_date: date
    end_date: date
