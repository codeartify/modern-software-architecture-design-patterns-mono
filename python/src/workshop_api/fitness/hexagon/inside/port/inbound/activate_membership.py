from typing import Protocol

from workshop_api.fitness.hexagon.inside.port.inbound.activate_membership_input import (
    ActivateMembershipInput,
)
from workshop_api.fitness.hexagon.inside.port.inbound.activate_membership_result import (
    ActivateMembershipResult,
)


class ForActivatingMemberships(Protocol):
    async def activate_membership(
        self,
        input_data: ActivateMembershipInput,
    ) -> ActivateMembershipResult:
        pass
