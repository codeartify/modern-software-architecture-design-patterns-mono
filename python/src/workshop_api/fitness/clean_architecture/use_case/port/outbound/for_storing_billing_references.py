from typing import Protocol

from workshop_api.fitness.clean_architecture.entity.membership_billing_reference import (
    MembershipBillingReference,
)


class ForStoringBillingReferences(Protocol):
    def store_membership_billing_reference(
        self,
        billing_reference: MembershipBillingReference,
    ) -> MembershipBillingReference:
        pass
