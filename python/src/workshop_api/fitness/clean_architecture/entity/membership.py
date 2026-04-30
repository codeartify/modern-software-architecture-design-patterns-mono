import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from ..use_case.exception import CustomerTooYoungException
from .customer import Customer


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

    @staticmethod
    def create(
        customer: Customer,
        plan_id: UUID,
        is_signed_by_custodian: bool | None,
        start_date: date,
        plan_duration_in_months: int,
        plan_price: Decimal,
    ) -> Membership:
        if customer.is_underage_at(start_date) and is_signed_by_custodian is not True:
            raise CustomerTooYoungException(
                "Customers younger than 18 require signedByCustodian=true"
            )

        end_date = Membership._plus_months(start_date, plan_duration_in_months)

        return Membership(
            id=uuid.uuid4(),
            customer_id=customer.id,
            plan_id=plan_id,
            plan_price=int(plan_price),
            plan_duration_in_months=plan_duration_in_months,
            status="ACTIVE",
            status_reason=None,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def _plus_months(start_date: date, months: int) -> date:
        import calendar

        total_month_index = start_date.month - 1 + months
        end_year = start_date.year + (total_month_index // 12)
        end_month = (total_month_index % 12) + 1
        end_day = min(start_date.day, calendar.monthrange(end_year, end_month)[1])
        return date(end_year, end_month, end_day)
