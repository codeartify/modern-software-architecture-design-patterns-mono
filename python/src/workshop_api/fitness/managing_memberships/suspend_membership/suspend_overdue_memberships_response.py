from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SuspendOverdueMembershipsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    checked_at: datetime = Field(alias="checkedAt", serialization_alias="checkedAt")
    checked_memberships: int = Field(
        alias="checkedMemberships",
        serialization_alias="checkedMemberships",
    )
    suspended_membership_ids: list[UUID] = Field(
        alias="suspendedMembershipIds",
        serialization_alias="suspendedMembershipIds",
    )
