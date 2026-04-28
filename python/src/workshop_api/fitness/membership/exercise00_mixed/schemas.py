from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class E00ActivateMembershipRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="customerId")
    plan_id: str = Field(alias="planId")
    signed_by_custodian: bool | None = Field(default=None, alias="signedByCustodian")


class E00ActivateMembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: str = Field(alias="membershipId", serialization_alias="membershipId")
    customer_id: str = Field(alias="customerId", serialization_alias="customerId")
    plan_id: str = Field(alias="planId", serialization_alias="planId")
    plan_price: int = Field(alias="planPrice", serialization_alias="planPrice")
    plan_duration: int = Field(alias="planDuration", serialization_alias="planDuration")
    status: str
    reason: str | None = None
    start_date: date = Field(alias="startDate", serialization_alias="startDate")
    end_date: date = Field(alias="endDate", serialization_alias="endDate")
    invoice_id: str = Field(alias="invoiceId", serialization_alias="invoiceId")
    external_invoice_id: str | None = Field(
        alias="externalInvoiceId",
        serialization_alias="externalInvoiceId",
    )
    invoice_due_date: date = Field(alias="invoiceDueDate", serialization_alias="invoiceDueDate")


class E00MembershipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    membership_id: str = Field(alias="membershipId", serialization_alias="membershipId")
    customer_id: str = Field(alias="customerId", serialization_alias="customerId")
    plan_id: str = Field(alias="planId", serialization_alias="planId")
    plan_price: int = Field(alias="planPrice", serialization_alias="planPrice")
    plan_duration: int = Field(alias="planDuration", serialization_alias="planDuration")
    status: str
    reason: str | None = None
    start_date: date = Field(alias="startDate", serialization_alias="startDate")
    end_date: date = Field(alias="endDate", serialization_alias="endDate")


class E00SuspendOverdueMembershipsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    checked_at: datetime | None = Field(default=None, alias="checkedAt")


class E00SuspendOverdueMembershipsResponse(BaseModel):
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
