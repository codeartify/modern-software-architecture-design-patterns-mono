from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from workshop_api.fitness.shared.external_invoice_provider.models import (
    ExternalInvoiceProviderStatus,
)


class ExternalInvoiceProviderUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_reference: str = Field(alias="customerReference")
    contract_reference: str = Field(alias="contractReference")
    amount_in_cents: int = Field(alias="amountInCents")
    currency: str
    due_date: date = Field(alias="dueDate")
    status: ExternalInvoiceProviderStatus
    description: str | None = None
    external_correlation_id: str | None = Field(
        default=None,
        alias="externalCorrelationId",
    )
    metadata: dict[str, str] | None = None


class ExternalInvoiceProviderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    invoice_id: str = Field(alias="invoiceId", serialization_alias="invoiceId")
    customer_reference: str = Field(
        alias="customerReference",
        serialization_alias="customerReference",
    )
    contract_reference: str = Field(
        alias="contractReference",
        serialization_alias="contractReference",
    )
    amount_in_cents: int = Field(alias="amountInCents", serialization_alias="amountInCents")
    currency: str
    due_date: date = Field(alias="dueDate", serialization_alias="dueDate")
    status: ExternalInvoiceProviderStatus
    description: str | None = None
    external_correlation_id: str | None = Field(
        default=None,
        alias="externalCorrelationId",
        serialization_alias="externalCorrelationId",
    )
    metadata: dict[str, str] | None = None
