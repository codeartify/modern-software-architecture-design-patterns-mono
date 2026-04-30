from enum import StrEnum


class MembershipStatusValue(StrEnum):
    ACTIVE = "ACTIVE"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"
