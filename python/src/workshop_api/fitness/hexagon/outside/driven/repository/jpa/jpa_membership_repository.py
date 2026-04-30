import uuid

from workshop_api.fitness.hexagon.inside.port.outbound.for_storing_memberships import (
    ForStoringMemberships,
)
from workshop_api.fitness.hexagon.inside.port.outbound.membership import Membership
from workshop_api.fitness.layered.infrastructure.membership_entity import MembershipOrmModel
from workshop_api.fitness.layered.infrastructure.membership_repository import (
    MembershipRepository,
)


class JpaMembershipRepository(ForStoringMemberships):
    def __init__(self, membership_repository: MembershipRepository) -> None:
        self.membership_repository = membership_repository

    def store_membership(self, membership: Membership) -> Membership:
        entity = MembershipOrmModel(
            id=str(membership.id),
            customer_id=str(membership.customer_id),
            plan_id=str(membership.plan_id),
            plan_price=membership.plan_price,
            plan_duration=membership.plan_duration_in_months,
            status=membership.status,
            reason=membership.status_reason,
            start_date=membership.start_date,
            end_date=membership.end_date,
        )

        stored_entity = self.membership_repository.save(entity)

        return Membership(
            id=uuid.UUID(stored_entity.id),
            customer_id=uuid.UUID(stored_entity.customer_id),
            plan_id=uuid.UUID(stored_entity.plan_id),
            plan_price=stored_entity.plan_price,
            plan_duration_in_months=stored_entity.plan_duration,
            status=stored_entity.status,
            status_reason=stored_entity.reason,
            start_date=stored_entity.start_date,
            end_date=stored_entity.end_date,
        )
