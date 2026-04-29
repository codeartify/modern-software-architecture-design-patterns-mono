from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from workshop_api.fitness.customer import database
from workshop_api.fitness.customer.database import Base
from workshop_api.fitness.customer.models import CustomerOrmModel
from workshop_api.fitness.membership.models import (
    MembershipBillingReferenceOrmModel,
    MembershipOrmModel,
)
from workshop_api.fitness.plan.models import PlanOrmModel


def test_seed_demo_data_populates_expected_workshop_records(tmp_path: Path, monkeypatch) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'seed-demo-data.db'}",
        connect_args={"check_same_thread": False},
    )
    test_sessionmaker = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(
        bind=test_engine,
        tables=[
            CustomerOrmModel.__table__,
            PlanOrmModel.__table__,
            MembershipOrmModel.__table__,
            MembershipBillingReferenceOrmModel.__table__,
        ],
    )
    monkeypatch.setattr(database, "SessionLocal", test_sessionmaker)

    database.seed_demo_data()
    database.seed_demo_data()

    session = test_sessionmaker()
    assert session.query(CustomerOrmModel).count() == 4
    assert session.query(PlanOrmModel).count() == 4
    assert session.query(MembershipOrmModel).count() == 5
    assert session.query(MembershipBillingReferenceOrmModel).count() == 5

    seeded_plan = session.get(PlanOrmModel, "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12")
    assert seeded_plan is not None
    assert seeded_plan.title == "Premium 12 Months"
    assert Decimal(str(seeded_plan.price)) == Decimal("999.00")

    seeded_membership = session.get(
        MembershipOrmModel, "b7000000-0000-0000-0000-000000000004"
    )
    assert seeded_membership is not None
    assert seeded_membership.status == "SUSPENDED"
    assert seeded_membership.reason == "NON_PAYMENT"

    seeded_billing_reference = session.get(
        MembershipBillingReferenceOrmModel, "c7000000-0000-0000-0000-000000000001"
    )
    assert seeded_billing_reference is not None
    assert seeded_billing_reference.external_invoice_id == "seed-external-open-overdue"
    assert seeded_billing_reference.external_invoice_reference == "seed-local-open-overdue"
    assert seeded_billing_reference.status == "OPEN"
    session.close()
