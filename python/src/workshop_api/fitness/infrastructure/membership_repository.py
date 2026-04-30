from uuid import UUID

from sqlalchemy.orm import Session

from workshop_api.fitness.infrastructure.membership_entity import MembershipOrmModel


class MembershipRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_all(self) -> list[MembershipOrmModel]:
        return self.session.query(MembershipOrmModel).all()

    def find_by_id(self, membership_id: UUID) -> MembershipOrmModel | None:
        return self.session.get(MembershipOrmModel, str(membership_id))

    def save(self, membership: MembershipOrmModel) -> MembershipOrmModel:
        self.session.add(membership)
        self.session.commit()
        self.session.refresh(membership)
        return membership
