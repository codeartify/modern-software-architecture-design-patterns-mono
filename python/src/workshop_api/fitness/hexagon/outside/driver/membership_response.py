from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class MembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: str = Field(alias="membershipId", serialization_alias="membershipId")
    customer_id: str = Field(alias="customerId", serialization_alias="customerId")
    plan_id: str = Field(alias="planId", serialization_alias="planId")
    plan_price: int = Field(alias="planPrice", serialization_alias="planPrice")
    plan_duration: int = Field(alias="planDuration", serialization_alias="planDuration")
    status: str
    reason: str | None = None
    start_date: date = Field(alias="startDate", serialization_alias="startDate")
    end_date: date = Field(alias="endDate", serialization_alias="endDate")
