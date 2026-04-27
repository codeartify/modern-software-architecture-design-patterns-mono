from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SharedPlanUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    description: str
    duration_in_months: int = Field(alias="durationInMonths")
    price: Decimal


class SharedPlanResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    description: str
    duration_in_months: int = Field(
        alias="durationInMonths",
        serialization_alias="durationInMonths",
    )
    price: Decimal
