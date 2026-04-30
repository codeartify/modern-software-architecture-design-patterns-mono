from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from workshop_api.fitness.managing_memberships.shared.membership_entity import MembershipOrmModel


class ListMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: UUID = Field(alias="membershipId", serialization_alias="membershipId")
    customer_id: UUID = Field(alias="customerId", serialization_alias="customerId")
    plan_id: UUID = Field(alias="planId", serialization_alias="planId")
    plan_price: int = Field(alias="planPrice", serialization_alias="planPrice")
    plan_duration: int = Field(alias="planDuration", serialization_alias="planDuration")
    status: str
    reason: str | None = None
    start_date: date = Field(alias="startDate", serialization_alias="startDate")
    end_date: date = Field(alias="endDate", serialization_alias="endDate")

    @staticmethod
    def from_entity(entity: MembershipOrmModel) -> ListMembershipResponse:
        return ListMembershipResponse(
            membershipId=entity.id,
            customerId=entity.customer_id,
            planId=entity.plan_id,
            planPrice=entity.plan_price,
            planDuration=entity.plan_duration,
            status=entity.status,
            reason=entity.reason,
            startDate=entity.start_date,
            endDate=entity.end_date,
        )
