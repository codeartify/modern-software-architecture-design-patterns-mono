from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class SharedCustomerUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    date_of_birth: date = Field(alias="dateOfBirth")
    email_address: str = Field(alias="emailAddress")


class SharedCustomerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    date_of_birth: date = Field(alias="dateOfBirth", serialization_alias="dateOfBirth")
    email_address: str = Field(alias="emailAddress", serialization_alias="emailAddress")
