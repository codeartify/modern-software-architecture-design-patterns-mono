from dataclasses import dataclass
from datetime import date

from .duration import Duration
from .plan_id import PlanId
from .price import Price


@dataclass(frozen=True)
class PlanDetails:
    plan_id: PlanId
    price: Price
    duration: Duration

    @property
    def plan_price(self) -> int:
        return self.price.amount

    @property
    def plan_duration_in_months(self) -> int:
        return self.duration.in_months()

    @property
    def start_date(self) -> date:
        return self.duration.start_date

    @property
    def end_date(self) -> date:
        return self.duration.end_date
