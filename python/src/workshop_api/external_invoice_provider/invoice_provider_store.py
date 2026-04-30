from workshop_api.external_invoice_provider.invoice_provider_schemas import (
    InvoiceProviderResponse,
    InvoiceProviderUpsertRequest,
)


class InvoiceProviderStore:
    def __init__(self) -> None:
        self._invoices: dict[str, InvoiceProviderResponse] = {}

    def find_all(self) -> list[InvoiceProviderResponse]:
        return list(self._invoices.values())

    def find_by_id(self, invoice_id: str) -> InvoiceProviderResponse | None:
        return self._invoices.get(invoice_id)

    def save(
        self,
        invoice_id: str,
        request: InvoiceProviderUpsertRequest,
    ) -> InvoiceProviderResponse:
        response = InvoiceProviderResponse(
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

    def save_response(
        self,
        response: InvoiceProviderResponse,
    ) -> InvoiceProviderResponse:
        self._invoices[response.invoice_id] = response
        return response

    def delete(self, invoice_id: str) -> None:
        self._invoices.pop(invoice_id, None)

    def clear(self) -> None:
        self._invoices.clear()
