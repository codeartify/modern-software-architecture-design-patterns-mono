from dataclasses import dataclass

from .membership_status_value import MembershipStatusValue


@dataclass(frozen=True)
class MembershipStatus:
    value: MembershipStatusValue
    reason: str | None
