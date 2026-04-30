from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SuspendOverdueMembershipsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    checked_at: datetime | None = Field(default=None, alias="checkedAt")
