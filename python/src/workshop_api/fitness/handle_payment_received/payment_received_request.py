from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaymentReceivedRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    external_invoice_id: str | None = Field(default=None, alias="externalInvoiceId")
    external_invoice_reference: str | None = Field(
        default=None,
        alias="externalInvoiceReference",
    )
    membership_id: str | None = Field(default=None, alias="membershipId")
    paid_at: datetime | None = Field(default=None, alias="paidAt")
