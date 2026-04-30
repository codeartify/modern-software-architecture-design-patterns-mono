from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class Plan:
    id: UUID
    price: Decimal
    duration_in_months: int
    title: str
