from workshop_api.fitness.external_invoice_provider.schemas import (
    ExternalInvoiceProviderResponse,
    ExternalInvoiceProviderUpsertRequest,
)


class ExternalInvoiceProviderStore:
    def __init__(self) -> None:
        self._invoices: dict[str, ExternalInvoiceProviderResponse] = {}

    def list_invoices(self) -> list[ExternalInvoiceProviderResponse]:
        return list(self._invoices.values())

    def get_invoice(self, invoice_id: str) -> ExternalInvoiceProviderResponse | None:
        return self._invoices.get(invoice_id)

    def save(
        self,
        invoice_id: str,
        request: ExternalInvoiceProviderUpsertRequest,
    ) -> ExternalInvoiceProviderResponse:
        response = ExternalInvoiceProviderResponse(
            invoiceId=invoice_id,
            customerReference=request.customer_reference,
            contractReference=request.contract_reference,
            amountInCents=request.amount_in_cents,
            currency=request.currency,
            dueDate=request.due_date,
            status=request.status,
            description=request.description,
            externalCorrelationId=request.external_correlation_id,
            metadata=request.metadata,
        )
        self._invoices[invoice_id] = response
        return response

    def delete(self, invoice_id: str) -> None:
        self._invoices.pop(invoice_id, None)

    def clear(self) -> None:
        self._invoices.clear()
