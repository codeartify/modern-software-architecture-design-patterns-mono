from uuid import UUID

from sqlalchemy.orm import Session

from workshop_api.fitness.infrastructure.plan_entity import PlanOrmModel


class PlanRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_all(self) -> list[PlanOrmModel]:
        return self.session.query(PlanOrmModel).all()

    def find_by_id(self, plan_id: UUID) -> PlanOrmModel | None:
        return self.session.get(PlanOrmModel, str(plan_id))

    def save(self, plan: PlanOrmModel) -> PlanOrmModel:
        self.session.add(plan)
        self.session.commit()
        self.session.refresh(plan)
        return plan

    def delete(self, plan: PlanOrmModel) -> None:
        self.session.delete(plan)
        self.session.commit()
