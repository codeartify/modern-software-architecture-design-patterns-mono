from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaymentReceivedResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    paid_at: datetime = Field(alias="paidAt", serialization_alias="paidAt")
    membership_id: UUID = Field(alias="membershipId", serialization_alias="membershipId")
    billing_reference_id: UUID = Field(
        alias="billingReferenceId",
        serialization_alias="billingReferenceId",
    )
    previous_membership_status: str = Field(
        alias="previousMembershipStatus",
        serialization_alias="previousMembershipStatus",
    )
    new_membership_status: str = Field(
        alias="newMembershipStatus",
        serialization_alias="newMembershipStatus",
    )
    reactivated: bool
    message: str
