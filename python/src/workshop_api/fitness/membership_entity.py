from __future__ import annotations

import uuid
from datetime import datetime

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
