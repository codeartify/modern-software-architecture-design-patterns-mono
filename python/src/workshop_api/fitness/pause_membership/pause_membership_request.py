from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PauseMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pause_start_date: date | None = Field(default=None, alias="pauseStartDate")
    pause_end_date: date | None = Field(default=None, alias="pauseEndDate")
    reason: str | None = None
