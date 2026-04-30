from typing import Protocol

from workshop_api.fitness.hexagon.inside.port.outbound.customer_activate_membership_email import (
    CustomerActivateMembershipEmail,
)


class ForSendingEmails(Protocol):
    def send_email(self, email: CustomerActivateMembershipEmail) -> None:
        pass
