from typing import Protocol

from .activate_membership_input import ActivateMembershipInput
from .activate_membership_result import ActivateMembershipResult


class ActivateMembershipUseCase(Protocol):
    async def activate_membership(
        self,
        input_data: ActivateMembershipInput,
    ) -> ActivateMembershipResult:
        pass
