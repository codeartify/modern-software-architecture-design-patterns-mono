from dataclasses import dataclass


@dataclass(frozen=True)
class ActivateMembershipInput:
    customer_id: str
    plan_id: str
    signed_by_custodian: bool | None
