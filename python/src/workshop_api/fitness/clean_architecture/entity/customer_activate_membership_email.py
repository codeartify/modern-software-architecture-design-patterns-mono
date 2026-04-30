from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CustomerActivateMembershipEmail:
    invoice_id: str
    invoice_due_date: date
    email_address: str
    plan_price: int
    email_template: str

    @staticmethod
    def to_email(
        billing_reference,
        email_address: str,
        plan_price: int,
    ) -> CustomerActivateMembershipEmail:
        email_template = """
|To: {to}
|From: {sender}
|Subject: Your Membership Invoice {invoice_id}
|
|Dear customer,
|
|Thank you for your membership.
|
|Please find your invoice details below:
|Invoice ID: {invoice_id}
|Amount Due: CHF {amount}
|Due Date: {due_date}
|
|Attachment: invoice-{invoice_id}.pdf
|
|Kind regards,
|Codeartify Billing
|"""
        return CustomerActivateMembershipEmail(
            invoice_id=billing_reference.external_invoice_reference,
            invoice_due_date=billing_reference.due_date,
            email_address=email_address,
            plan_price=plan_price,
            email_template=email_template,
        )
