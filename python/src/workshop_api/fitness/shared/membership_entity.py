from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy import Column, Date, DateTime, Integer, String

from workshop_api.fitness.database import Base


class MembershipOrmModel(Base):
    __tablename__ = "memberships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=False)
    plan_id = Column(String(36), nullable=False)
    plan_price = Column(Integer, nullable=False)
    plan_duration = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)
    reason = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    pause_start_date = Column(Date, nullable=True)
    pause_end_date = Column(Date, nullable=True)
    pause_reason = Column(String(100), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String(100), nullable=True)

    def is_active(self) -> bool:
        return self.status == "ACTIVE"

    def is_paused(self) -> bool:
        return self.status == "PAUSED"

    def is_suspended(self) -> bool:
        return self.status == "SUSPENDED"

    def is_suspended_for_non_payment(self) -> bool:
        return self.is_suspended() and self.reason == "NON_PAYMENT"

    def is_cancelled(self) -> bool:
        return self.status == "CANCELLED"

    def suspend_for_non_payment(self) -> None:
        self.status = "SUSPENDED"
        self.reason = "NON_PAYMENT"

    def reactivate_after_payment(self) -> None:
        self.status = "ACTIVE"
        self.reason = None

    def pause(self, pause_start_date, pause_end_date, reason: str | None) -> None:
        pause_days = (pause_end_date - pause_start_date).days + 1
        self.status = "PAUSED"
        self.pause_start_date = pause_start_date
        self.pause_end_date = pause_end_date
        self.pause_reason = reason
        self.end_date = self.end_date + timedelta(days=pause_days)

    def resume_after_pause(self) -> None:
        self.status = "ACTIVE"
        self.pause_start_date = None
        self.pause_end_date = None
        self.pause_reason = None

    def cancel(self, cancelled_at, reason: str | None) -> None:
        self.status = "CANCELLED"
        self.cancelled_at = cancelled_at
        self.cancellation_reason = reason

    def extend_by(self, additional_months: int, additional_days: int) -> None:
        month_index = self.end_date.month - 1 + additional_months
        year = self.end_date.year + month_index // 12
        month = month_index % 12 + 1
        import calendar

        day = min(self.end_date.day, calendar.monthrange(year, month)[1])
        self.end_date = self.end_date.replace(year=year, month=month, day=day)
        self.end_date = self.end_date + timedelta(days=additional_days)


class MembershipBillingReferenceOrmModel(Base):
    __tablename__ = "membership_billing_references"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    membership_id = Column(String(36), nullable=False)
    external_invoice_id = Column(String(100), nullable=False, unique=True)
    external_invoice_reference = Column(String(100), nullable=False, unique=True)
    due_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def is_paid(self) -> bool:
        return self.status == "PAID"

    def mark_paid(self, paid_at) -> None:
        self.status = "PAID"
        self.updated_at = paid_at
