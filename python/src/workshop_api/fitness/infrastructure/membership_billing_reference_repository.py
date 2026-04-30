from sqlalchemy.orm import Session

from workshop_api.fitness.infrastructure.membership_entity import (
    MembershipBillingReferenceOrmModel,
)


class MembershipBillingReferenceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(
        self,
        billing_reference: MembershipBillingReferenceOrmModel,
    ) -> MembershipBillingReferenceOrmModel:
        self.session.add(billing_reference)
        self.session.commit()
        self.session.refresh(billing_reference)
        return billing_reference
