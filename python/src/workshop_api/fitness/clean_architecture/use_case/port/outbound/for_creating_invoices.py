from typing import Protocol

from workshop_api.fitness.clean_architecture.entity.membership_invoice_details import (
    MembershipInvoiceDetails,
)


class ForCreatingInvoices(Protocol):
    async def create_invoice_with(self, invoice: MembershipInvoiceDetails) -> str:
        pass
