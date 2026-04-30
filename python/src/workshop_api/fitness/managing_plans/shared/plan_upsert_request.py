from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PlanUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    description: str
    duration_in_months: int = Field(alias="durationInMonths")
    price: Decimal
