from __future__ import annotations

import uuid

from sqlalchemy import Column, Date, Integer, String

from workshop_api.fitness.customer.database import Base


class E00MembershipOrmModel(Base):
    __tablename__ = "memberships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), nullable=False)
    plan_id = Column(String(36), nullable=False)
    plan_price = Column(Integer, nullable=False)
    plan_duration = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
