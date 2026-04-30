import json
from datetime import date
from typing import Any

import httpx

from workshop_api.fitness.infrastructure.external_invoice_provider_response import (
    ExternalInvoiceProviderResponse,
    ExternalInvoiceProviderUpsertRequest,
)
from workshop_api.fitness.infrastructure.external_invoice_provider_status import (
    ExternalInvoiceProviderStatus,
)
from workshop_api.fitness.infrastructure.membership_entity import MembershipOrmModel
from workshop_api.fitness.infrastructure.plan_entity import PlanOrmModel


class ExternalInvoiceProviderClient:
    def __init__(self, base_url: str, app: Any | None = None) -> None:
        self.base_url = base_url
        self.app = app

    async def create_membership_invoice(
        self,
        customer_id: str,
        membership: MembershipOrmModel,
        plan: PlanOrmModel,
        invoice_due_date: date,
        invoice_id: str,
    ) -> str:
        external_invoice_request = ExternalInvoiceProviderUpsertRequest(
            customerReference=customer_id,
            contractReference=membership.id,
            amountInCents=membership.plan_price,
            currency="CHF",
            dueDate=invoice_due_date,
            status=ExternalInvoiceProviderStatus.OPEN,
            description=f"Membership invoice for {plan.title}",
            externalCorrelationId=invoice_id,
            metadata={
                "exercise": "membership",
                "planId": membership.plan_id,
            },
        )

        client_kwargs: dict[str, object] = {"base_url": self.base_url}
        if self.base_url.startswith("http://testserver") and self.app is not None:
            client_kwargs["transport"] = httpx.ASGITransport(app=self.app)

        async with httpx.AsyncClient(**client_kwargs) as client:
            response = await client.post(
                "/api/shared/external-invoice-provider/invoices",
                json=json.loads(
                    external_invoice_request.model_dump_json(by_alias=True)
                    if hasattr(external_invoice_request, "model_dump_json")
                    else external_invoice_request.json(by_alias=True)
                ),
            )
            response.raise_for_status()
            external_invoice = (
                ExternalInvoiceProviderResponse.model_validate(response.json())
                if hasattr(ExternalInvoiceProviderResponse, "model_validate")
                else ExternalInvoiceProviderResponse.parse_obj(response.json())
            )

        return external_invoice.invoice_id if external_invoice is not None else invoice_id
