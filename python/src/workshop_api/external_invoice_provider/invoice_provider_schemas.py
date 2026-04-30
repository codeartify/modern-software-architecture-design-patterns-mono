from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from workshop_api.external_invoice_provider.invoice_provider_status import (
    InvoiceProviderStatus,
)


class InvoiceProviderUpsertRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_reference: str = Field(alias="customerReference")
    contract_reference: str = Field(alias="contractReference")
    amount_in_cents: int = Field(alias="amountInCents")
    currency: str
    due_date: date = Field(alias="dueDate")
    status: InvoiceProviderStatus
    description: str | None = None
    external_correlation_id: str | None = Field(
        default=None,
        alias="externalCorrelationId",
    )
    metadata: dict[str, str] | None = None


class InvoiceProviderResponse(BaseModel):
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
    status: InvoiceProviderStatus
    description: str | None = None
    external_correlation_id: str | None = Field(
        default=None,
        alias="externalCorrelationId",
        serialization_alias="externalCorrelationId",
    )
    metadata: dict[str, str] | None = None


class InvoiceProviderPaymentReceivedCallbackRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    external_invoice_id: str | None = Field(
        default=None,
        alias="externalInvoiceId",
        serialization_alias="externalInvoiceId",
    )
    external_invoice_reference: str | None = Field(
        default=None,
        alias="externalInvoiceReference",
        serialization_alias="externalInvoiceReference",
    )
    membership_id: str | None = Field(
        default=None,
        alias="membershipId",
        serialization_alias="membershipId",
    )
    paid_at: datetime = Field(alias="paidAt", serialization_alias="paidAt")
