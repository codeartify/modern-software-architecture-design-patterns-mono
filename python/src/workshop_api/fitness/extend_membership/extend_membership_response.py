from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExtendMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: UUID = Field(alias="membershipId", serialization_alias="membershipId")
    status: str
    previous_end_date: date = Field(alias="previousEndDate", serialization_alias="previousEndDate")
    new_end_date: date = Field(alias="newEndDate", serialization_alias="newEndDate")
    billable: bool
    billing_reference_id: UUID | None = Field(
        default=None,
        alias="billingReferenceId",
        serialization_alias="billingReferenceId",
    )
    external_invoice_reference: str | None = Field(
        default=None,
        alias="externalInvoiceReference",
        serialization_alias="externalInvoiceReference",
    )
    external_invoice_id: str | None = Field(
        default=None,
        alias="externalInvoiceId",
        serialization_alias="externalInvoiceId",
    )
    invoice_due_date: date | None = Field(
        default=None,
        alias="invoiceDueDate",
        serialization_alias="invoiceDueDate",
    )
    message: str
