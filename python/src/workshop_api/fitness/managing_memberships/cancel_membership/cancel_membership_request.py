from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CancelMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cancelled_at: datetime | None = Field(default=None, alias="cancelledAt")
    reason: str | None = None
