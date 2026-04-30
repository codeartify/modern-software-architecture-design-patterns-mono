from pydantic import BaseModel, ConfigDict, Field


class ActivateMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    plan_id: str = Field(alias="planId")
    signed_by_custodian: bool | None = Field(default=None, alias="signedByCustodian")
