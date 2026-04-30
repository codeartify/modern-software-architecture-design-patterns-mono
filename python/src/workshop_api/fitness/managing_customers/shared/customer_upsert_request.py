from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CustomerUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    date_of_birth: date = Field(alias="dateOfBirth")
    email_address: str = Field(alias="emailAddress")
