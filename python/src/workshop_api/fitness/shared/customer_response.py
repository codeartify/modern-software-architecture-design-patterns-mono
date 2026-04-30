from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from workshop_api.fitness.shared.customer_entity import CustomerOrmModel


class CustomerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    date_of_birth: date = Field(alias="dateOfBirth", serialization_alias="dateOfBirth")
    email_address: str = Field(alias="emailAddress", serialization_alias="emailAddress")

    @staticmethod
    def from_entity(entity: CustomerOrmModel) -> CustomerResponse:
        return CustomerResponse(
            id=entity.id,
            name=entity.name,
            dateOfBirth=entity.date_of_birth,
            emailAddress=entity.email_address,
        )
