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


class PauseMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pause_start_date: date | None = Field(default=None, alias="pauseStartDate")
    pause_end_date: date | None = Field(default=None, alias="pauseEndDate")
    reason: str | None = None


class PauseMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: str = Field(alias="membershipId", serialization_alias="membershipId")
    previous_status: str = Field(alias="previousStatus", serialization_alias="previousStatus")
    new_status: str = Field(alias="newStatus", serialization_alias="newStatus")
    pause_start_date: date = Field(
        alias="pauseStartDate",
        serialization_alias="pauseStartDate",
    )
    pause_end_date: date = Field(alias="pauseEndDate", serialization_alias="pauseEndDate")
    previous_end_date: date = Field(
        alias="previousEndDate",
        serialization_alias="previousEndDate",
    )
    new_end_date: date = Field(alias="newEndDate", serialization_alias="newEndDate")
    reason: str | None = None
    message: str


class ResumeMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resumed_at: datetime | None = Field(default=None, alias="resumedAt")
    reason: str | None = None


class ResumeMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: str = Field(alias="membershipId", serialization_alias="membershipId")
    previous_status: str = Field(alias="previousStatus", serialization_alias="previousStatus")
    new_status: str = Field(alias="newStatus", serialization_alias="newStatus")
    resumed_at: datetime = Field(alias="resumedAt", serialization_alias="resumedAt")
    previous_pause_start_date: date | None = Field(
        alias="previousPauseStartDate",
        serialization_alias="previousPauseStartDate",
    )
    previous_pause_end_date: date | None = Field(
        alias="previousPauseEndDate",
        serialization_alias="previousPauseEndDate",
    )
    end_date: date = Field(alias="endDate", serialization_alias="endDate")
    reason: str | None = None
    message: str


class CancelMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cancelled_at: datetime | None = Field(default=None, alias="cancelledAt")
    reason: str | None = None


class CancelMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: str = Field(alias="membershipId", serialization_alias="membershipId")
    previous_status: str = Field(alias="previousStatus", serialization_alias="previousStatus")
    new_status: str = Field(alias="newStatus", serialization_alias="newStatus")
    cancelled_at: datetime = Field(alias="cancelledAt", serialization_alias="cancelledAt")
    reason: str | None = None
    message: str


class ExtendMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    additional_months: int | None = Field(default=None, alias="additionalMonths")
    additional_days: int | None = Field(default=None, alias="additionalDays")
    billable: bool | None = None
    price: int | None = None
    reason: str | None = None


class ExtendMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: str = Field(alias="membershipId", serialization_alias="membershipId")
    status: str
    previous_end_date: date = Field(
        alias="previousEndDate",
        serialization_alias="previousEndDate",
    )
    new_end_date: date = Field(alias="newEndDate", serialization_alias="newEndDate")
    billable: bool
    billing_reference_id: str | None = Field(
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
