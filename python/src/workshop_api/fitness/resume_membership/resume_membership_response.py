from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResumeMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: UUID = Field(alias="membershipId", serialization_alias="membershipId")
    previous_status: str = Field(alias="previousStatus", serialization_alias="previousStatus")
    new_status: str = Field(alias="newStatus", serialization_alias="newStatus")
    resumed_at: datetime = Field(alias="resumedAt", serialization_alias="resumedAt")
    previous_pause_start_date: date | None = Field(
        alias="previousPauseStartDate",
        serialization_alias="previousPauseStartDate",
    )
    previous_pause_end_date: date | None = Field(
        alias="previousPauseEndDate",
        serialization_alias="previousPauseEndDate",
    )
    end_date: date = Field(alias="endDate", serialization_alias="endDate")
    reason: str | None = None
    message: str
