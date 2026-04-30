from __future__ import annotations

import uuid

from sqlalchemy import Column, Integer, Numeric, String

from workshop_api.fitness.database import Base


class PlanOrmModel(Base):
    __tablename__ = "plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(String(2000), nullable=False)
    duration_in_months = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
