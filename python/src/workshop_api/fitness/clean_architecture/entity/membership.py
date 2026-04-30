import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from ..use_case.exception import CustomerTooYoungException
from .customer import Customer
from .customer_id import CustomerId
from .duration import Duration
from .membership_id import MembershipId
from .membership_status import MembershipStatus
from .membership_status_value import MembershipStatusValue
from .plan_details import PlanDetails
from .plan_id import PlanId
from .price import Price


@dataclass(frozen=True, init=False)
class Membership:
    _id: MembershipId
    _customer_id: CustomerId
    _status: MembershipStatus
    _plan_details: PlanDetails

    def __init__(
        self,
        id: MembershipId,
        customer_id: CustomerId,
        status: MembershipStatus,
        plan_details: PlanDetails,
    ) -> None:
        object.__setattr__(self, "_id", id)
        object.__setattr__(self, "_customer_id", customer_id)
        object.__setattr__(self, "_status", status)
        object.__setattr__(self, "_plan_details", plan_details)

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
            id=MembershipId(uuid.uuid4()),
            customer_id=CustomerId(customer.id),
            status=MembershipStatus(MembershipStatusValue.ACTIVE, None),
            plan_details=PlanDetails(
                PlanId(plan_id),
                Price(int(plan_price)),
                Duration(start_date, end_date),
            ),
        )

    @property
    def id(self) -> UUID:
        return self._id.id

    @property
    def customer_id(self) -> UUID:
        return self._customer_id.id

    @property
    def plan_id(self) -> UUID:
        return self._plan_details.plan_id.id

    @property
    def plan_price(self) -> int:
        return self._plan_details.plan_price

    @property
    def plan_duration_in_months(self) -> int:
        return self._plan_details.plan_duration_in_months

    @property
    def status(self) -> str:
        return self._status.value.value

    @property
    def status_reason(self) -> str | None:
        return self._status.reason

    @property
    def start_date(self) -> date:
        return self._plan_details.start_date

    @property
    def end_date(self) -> date:
        return self._plan_details.end_date

    @staticmethod
    def _plus_months(start_date: date, months: int) -> date:
        import calendar

        total_month_index = start_date.month - 1 + months
        end_year = start_date.year + (total_month_index // 12)
        end_month = (total_month_index % 12) + 1
        end_day = min(start_date.day, calendar.monthrange(end_year, end_month)[1])
        return date(end_year, end_month, end_day)
