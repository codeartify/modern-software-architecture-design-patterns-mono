from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from workshop_api.fitness.managing_plans.shared.plan_entity import PlanOrmModel


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

    @staticmethod
    def from_entity(entity: PlanOrmModel) -> PlanResponse:
        return PlanResponse(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            durationInMonths=entity.duration_in_months,
            price=entity.price,
        )
