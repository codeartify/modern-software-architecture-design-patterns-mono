from workshop_api.fitness.layered.infrastructure.in_memory_email_service import (
    InMemoryEmailService,
)

from ....entity import CustomerActivateMembershipEmail
from ....use_case.port.outbound import (
    ForSendingEmails,
)


class InMemoryMailSender(ForSendingEmails):
    def __init__(
        self,
        email_service: InMemoryEmailService,
        billing_sender_email_address: str,
    ) -> None:
        self.email_service = email_service
        self.billing_sender_email_address = billing_sender_email_address

    def send_email(self, email_details: CustomerActivateMembershipEmail) -> None:
        activation_email = (
            email_details.email_template.format(
                to=email_details.email_address,
                sender=self.billing_sender_email_address,
                invoice_id=email_details.invoice_id,
                amount=email_details.plan_price,
                due_date=email_details.invoice_due_date,
            )
            .replace("\n|", "\n")
            .strip()
        )

        print(activation_email)
        self.email_service.send(activation_email)
