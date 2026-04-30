from typing import Protocol

from workshop_api.fitness.hexagon.inside.port.outbound.membership import Membership


class ForStoringMemberships(Protocol):
    def store_membership(self, membership: Membership) -> Membership:
        pass
