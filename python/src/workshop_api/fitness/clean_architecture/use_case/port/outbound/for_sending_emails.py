from typing import Protocol

from workshop_api.fitness.clean_architecture.entity.customer_activate_membership_email import (
    CustomerActivateMembershipEmail,
)


class ForSendingEmails(Protocol):
    def send_email(self, email: CustomerActivateMembershipEmail) -> None:
        pass
