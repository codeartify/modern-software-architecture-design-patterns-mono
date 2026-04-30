import json
from typing import Any

import httpx

from ....entity import MembershipInvoiceDetails
from ....use_case.port.outbound import ForCreatingInvoices
from .external_invoice_provider_response import (
    ExternalInvoiceProviderResponse,
    ExternalInvoiceProviderUpsertRequest,
)
from .external_invoice_provider_status import ExternalInvoiceProviderStatus


class ExternalInvoiceRepository(ForCreatingInvoices):
    def __init__(self, base_url: str, app: Any | None = None) -> None:
        self.base_url = base_url
        self.app = app

    async def create_invoice_with(self, invoice: MembershipInvoiceDetails) -> str:
        request = ExternalInvoiceProviderUpsertRequest(
            customerReference=str(invoice.customer_id),
            contractReference=str(invoice.membership_id),
            amountInCents=int(invoice.plan_price),
            currency="CHF",
            dueDate=invoice.due_date,
            status=ExternalInvoiceProviderStatus.OPEN,
            description=f"Membership invoice for {invoice.plan_title}",
            externalCorrelationId=str(invoice.membership_id),
            metadata={
                "exercise": "membership",
                "planId": str(invoice.plan_id),
            },
        )

        client_kwargs: dict[str, object] = {"base_url": self.base_url}
        if self.base_url.startswith("http://testserver") and self.app is not None:
            client_kwargs["transport"] = httpx.ASGITransport(app=self.app)

        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.post(
                "/api/shared/external-invoice-provider/invoices",
                json=json.loads(
                    request.model_dump_json(by_alias=True)
                    if hasattr(request, "model_dump_json")
                    else request.json(by_alias=True)
                ),
            )
            response.raise_for_status()
            external_invoice = (
                ExternalInvoiceProviderResponse.model_validate(response.json())
                if hasattr(ExternalInvoiceProviderResponse, "model_validate")
                else ExternalInvoiceProviderResponse.parse_obj(response.json())
            )

        return (
            str(invoice.membership_id)
            if external_invoice is None
            else external_invoice.invoice_id
        )
