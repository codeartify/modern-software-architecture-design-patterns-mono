from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ActivateMembershipInput:
    customer_id: UUID
    plan_id: UUID
    signed_by_custodian: bool | None
