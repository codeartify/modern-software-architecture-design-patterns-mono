from pydantic import BaseModel, ConfigDict, Field


class ExtendMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    additional_months: int | None = Field(default=None, alias="additionalMonths")
    additional_days: int | None = Field(default=None, alias="additionalDays")
    billable: bool | None = None
    price: int | None = None
    reason: str | None = None
