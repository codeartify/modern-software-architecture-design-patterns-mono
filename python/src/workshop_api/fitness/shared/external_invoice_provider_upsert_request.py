from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from workshop_api.fitness.shared.invoice_provider_status import ExternalInvoiceProviderStatus


class ExternalInvoiceProviderUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_reference: str = Field(alias="customerReference")
    contract_reference: str = Field(alias="contractReference")
    amount_in_cents: int = Field(alias="amountInCents")
    currency: str
    due_date: date = Field(alias="dueDate")
    status: ExternalInvoiceProviderStatus
    description: str | None = None
    external_correlation_id: str | None = Field(default=None, alias="externalCorrelationId")
    metadata: dict[str, str] | None = None
