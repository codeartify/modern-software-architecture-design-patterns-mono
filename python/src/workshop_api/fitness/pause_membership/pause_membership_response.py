from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PauseMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: UUID = Field(alias="membershipId", serialization_alias="membershipId")
    previous_status: str = Field(alias="previousStatus", serialization_alias="previousStatus")
    new_status: str = Field(alias="newStatus", serialization_alias="newStatus")
    pause_start_date: date = Field(alias="pauseStartDate", serialization_alias="pauseStartDate")
    pause_end_date: date = Field(alias="pauseEndDate", serialization_alias="pauseEndDate")
    previous_end_date: date = Field(alias="previousEndDate", serialization_alias="previousEndDate")
    new_end_date: date = Field(alias="newEndDate", serialization_alias="newEndDate")
    reason: str | None = None
    message: str
