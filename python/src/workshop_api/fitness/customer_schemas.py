from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    date_of_birth: date = Field(alias="dateOfBirth")
    email_address: str = Field(alias="emailAddress")


class CustomerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    date_of_birth: date = Field(alias="dateOfBirth", serialization_alias="dateOfBirth")
    email_address: str = Field(alias="emailAddress", serialization_alias="emailAddress")
