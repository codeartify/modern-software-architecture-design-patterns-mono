from __future__ import annotations

import uuid

from sqlalchemy import Column, Date, String

from workshop_api.fitness.layered.infrastructure.database import Base


class CustomerOrmModel(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    email_address = Column(String(255), nullable=False, unique=True)
