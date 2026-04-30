from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CancelMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: UUID = Field(alias="membershipId", serialization_alias="membershipId")
    previous_status: str = Field(alias="previousStatus", serialization_alias="previousStatus")
    new_status: str = Field(alias="newStatus", serialization_alias="newStatus")
    cancelled_at: datetime = Field(alias="cancelledAt", serialization_alias="cancelledAt")
    reason: str | None = None
    message: str
