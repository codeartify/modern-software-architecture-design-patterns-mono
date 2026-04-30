import uuid

from workshop_api.fitness.layered.infrastructure.membership_entity import MembershipOrmModel
from workshop_api.fitness.layered.infrastructure.membership_repository import (
    MembershipRepository,
)

from ....entity import (
    CustomerId,
    Duration,
    Membership,
    MembershipId,
    MembershipStatus,
    MembershipStatusValue,
    PlanDetails,
    PlanId,
    Price,
)
from ....use_case.port.outbound import (
    ForStoringMemberships,
)


class SqlAlchemyMembershipRepository(ForStoringMemberships):
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
            id=MembershipId(uuid.UUID(stored_entity.id)),
            customer_id=CustomerId(uuid.UUID(stored_entity.customer_id)),
            status=MembershipStatus(
                MembershipStatusValue(stored_entity.status.upper()),
                stored_entity.reason,
            ),
            plan_details=PlanDetails(
                PlanId(uuid.UUID(stored_entity.plan_id)),
                Price(stored_entity.plan_price),
                Duration(stored_entity.start_date, stored_entity.end_date),
            ),
        )
