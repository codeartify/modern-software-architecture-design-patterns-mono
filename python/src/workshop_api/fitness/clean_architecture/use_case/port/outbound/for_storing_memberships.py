from typing import Protocol

from workshop_api.fitness.clean_architecture.entity.membership import Membership


class ForStoringMemberships(Protocol):
    def store_membership(self, membership: Membership) -> Membership:
        pass
