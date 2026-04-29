from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActivateMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: UUID = Field(alias="customerId")
    plan_id: UUID = Field(alias="planId")
    signed_by_custodian: bool | None = Field(default=None, alias="signedByCustodian")


class ActivateMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: UUID = Field(alias="membershipId", serialization_alias="membershipId")
    customer_id: UUID = Field(alias="customerId", serialization_alias="customerId")
    plan_id: UUID = Field(alias="planId", serialization_alias="planId")
    plan_price: int = Field(alias="planPrice", serialization_alias="planPrice")
    plan_duration: int = Field(alias="planDuration", serialization_alias="planDuration")
    status: str
    reason: str | None = None
    start_date: date = Field(alias="startDate", serialization_alias="startDate")
    end_date: date = Field(alias="endDate", serialization_alias="endDate")
    invoice_id: UUID = Field(alias="invoiceId", serialization_alias="invoiceId")
    external_invoice_id: str | None = Field(
        alias="externalInvoiceId",
        serialization_alias="externalInvoiceId",
    )
    invoice_due_date: date = Field(alias="invoiceDueDate", serialization_alias="invoiceDueDate")


class MembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: UUID = Field(alias="membershipId", serialization_alias="membershipId")
    customer_id: UUID = Field(alias="customerId", serialization_alias="customerId")
    plan_id: UUID = Field(alias="planId", serialization_alias="planId")
    plan_price: int = Field(alias="planPrice", serialization_alias="planPrice")
    plan_duration: int = Field(alias="planDuration", serialization_alias="planDuration")
    status: str
    reason: str | None = None
    start_date: date = Field(alias="startDate", serialization_alias="startDate")
    end_date: date = Field(alias="endDate", serialization_alias="endDate")


class SuspendOverdueMembershipsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    checked_at: datetime | None = Field(default=None, alias="checkedAt")


class SuspendOverdueMembershipsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    checked_at: datetime = Field(alias="checkedAt", serialization_alias="checkedAt")
    checked_memberships: int = Field(
        alias="checkedMemberships",
        serialization_alias="checkedMemberships",
    )
    suspended_membership_ids: list[str] = Field(
        alias="suspendedMembershipIds",
        serialization_alias="suspendedMembershipIds",
    )


class PaymentReceivedRequest(BaseModel):
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
    paid_at: datetime | None = Field(
        default=None,
        alias="paidAt",
        serialization_alias="paidAt",
    )


class PaymentReceivedResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    paid_at: datetime = Field(alias="paidAt", serialization_alias="paidAt")
    membership_id: str = Field(alias="membershipId", serialization_alias="membershipId")
    billing_reference_id: str = Field(
        alias="billingReferenceId",
        serialization_alias="billingReferenceId",
    )
    previous_membership_status: str = Field(
        alias="previousMembershipStatus",
        serialization_alias="previousMembershipStatus",
    )
    new_membership_status: str = Field(
        alias="newMembershipStatus",
        serialization_alias="newMembershipStatus",
    )
    reactivated: bool
    message: str
