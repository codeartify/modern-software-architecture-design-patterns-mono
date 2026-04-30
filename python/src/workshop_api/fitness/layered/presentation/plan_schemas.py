from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlanUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    description: str
    duration_in_months: int = Field(alias="durationInMonths")
    price: Decimal


class PlanResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    title: str
    description: str
    duration_in_months: int = Field(
        alias="durationInMonths",
        serialization_alias="durationInMonths",
    )
    price: Decimal
