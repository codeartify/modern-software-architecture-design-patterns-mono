from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resumed_at: datetime | None = Field(default=None, alias="resumedAt")
    reason: str | None = None
