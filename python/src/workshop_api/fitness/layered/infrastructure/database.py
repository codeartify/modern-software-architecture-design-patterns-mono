import os
from collections.abc import Generator
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

try:
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        pass
except ImportError:
    from sqlalchemy.orm import declarative_base

    Base: Any = declarative_base()


ROOT_DIR = Path(__file__).resolve().parents[6]
DATABASE_DIR = ROOT_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'workshop-python.db'}"
DATABASE_URL = os.getenv("WORKSHOP_PYTHON_DATABASE_URL", DEFAULT_DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db_session() -> Generator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def seed_demo_data() -> None:
    from workshop_api.fitness.layered.infrastructure.customer_entity import CustomerOrmModel
    from workshop_api.fitness.layered.infrastructure.membership_entity import (
        MembershipBillingReferenceOrmModel,
        MembershipOrmModel,
    )
    from workshop_api.fitness.layered.infrastructure.plan_entity import PlanOrmModel

    seeded_at = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)
    updated_paid_at = datetime(2026, 2, 1, 10, 0, tzinfo=UTC)
    session = SessionLocal()
    try:
        for customer in [
            CustomerOrmModel(
                id="11111111-1111-1111-1111-111111111111",
                name="Alice Active",
                date_of_birth=date(1986, 8, 13),
                email_address="alice.active@example.com",
            ),
            CustomerOrmModel(
                id="22222222-2222-2222-2222-222222222222",
                name="Bob Builder",
                date_of_birth=date(1992, 4, 21),
                email_address="bob.builder@example.com",
            ),
            CustomerOrmModel(
                id="33333333-3333-3333-3333-333333333333",
                name="Carla Coach",
                date_of_birth=date(1978, 11, 5),
                email_address="carla.coach@example.com",
            ),
            CustomerOrmModel(
                id="44444444-4444-4444-4444-444444444444",
                name="Mila Minor",
                date_of_birth=date(2010, 9, 14),
                email_address="mila.minor@example.com",
            ),
        ]:
            session.merge(customer)

        for plan in [
            PlanOrmModel(
                id="aaaaaaa1-aaaa-aaaa-aaaa-aaaaaaaaaaa1",
                title="Basic 1 Month",
                description="Flexible monthly membership plan",
                duration_in_months=1,
                price=Decimal("129.00"),
            ),
            PlanOrmModel(
                id="aaaaaaa6-aaaa-aaaa-aaaa-aaaaaaaaaaa6",
                title="Standard 6 Months",
                description="Six-month commitment with reduced monthly price",
                duration_in_months=6,
                price=Decimal("599.00"),
            ),
            PlanOrmModel(
                id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                title="Premium 12 Months",
                description="Twelve-month plan for regular training",
                duration_in_months=12,
                price=Decimal("999.00"),
            ),
            PlanOrmModel(
                id="aaaaaa24-aaaa-aaaa-aaaa-aaaaaaaaaa24",
                title="Elite 24 Months",
                description="Twenty-four-month plan for long-term training",
                duration_in_months=24,
                price=Decimal("1699.00"),
            ),
        ]:
            session.merge(plan)

        for membership in [
            MembershipOrmModel(
                id="b7000000-0000-0000-0000-000000000001",
                customer_id="11111111-1111-1111-1111-111111111111",
                plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                plan_price=999,
                plan_duration=12,
                status="ACTIVE",
                reason=None,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
            ),
            MembershipOrmModel(
                id="b7000000-0000-0000-0000-000000000002",
                customer_id="22222222-2222-2222-2222-222222222222",
                plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                plan_price=999,
                plan_duration=12,
                status="ACTIVE",
                reason=None,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
            ),
            MembershipOrmModel(
                id="b7000000-0000-0000-0000-000000000003",
                customer_id="33333333-3333-3333-3333-333333333333",
                plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                plan_price=999,
                plan_duration=12,
                status="ACTIVE",
                reason=None,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
            ),
            MembershipOrmModel(
                id="b7000000-0000-0000-0000-000000000004",
                customer_id="11111111-1111-1111-1111-111111111111",
                plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                plan_price=999,
                plan_duration=12,
                status="SUSPENDED",
                reason="NON_PAYMENT",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
            ),
            MembershipOrmModel(
                id="b7000000-0000-0000-0000-000000000005",
                customer_id="22222222-2222-2222-2222-222222222222",
                plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                plan_price=999,
                plan_duration=12,
                status="CANCELLED",
                reason=None,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
                cancelled_at=updated_paid_at,
                cancellation_reason="Seed cancellation",
            ),
            MembershipOrmModel(
                id="b7000000-0000-0000-0000-000000000006",
                customer_id="33333333-3333-3333-3333-333333333333",
                plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                plan_price=999,
                plan_duration=12,
                status="PAUSED",
                reason=None,
                start_date=date(2026, 1, 1),
                end_date=date(2027, 1, 14),
                pause_start_date=date(2026, 6, 1),
                pause_end_date=date(2026, 6, 14),
                pause_reason="Seed pause",
            ),
        ]:
            session.merge(membership)

        for billing_reference in [
            MembershipBillingReferenceOrmModel(
                id="c7000000-0000-0000-0000-000000000001",
                membership_id="b7000000-0000-0000-0000-000000000001",
                external_invoice_id="seed-external-open-overdue",
                external_invoice_reference="seed-local-open-overdue",
                due_date=date(2026, 5, 1),
                status="OPEN",
                created_at=seeded_at,
                updated_at=seeded_at,
            ),
            MembershipBillingReferenceOrmModel(
                id="c7000000-0000-0000-0000-000000000002",
                membership_id="b7000000-0000-0000-0000-000000000002",
                external_invoice_id="seed-external-open-current",
                external_invoice_reference="seed-local-open-current",
                due_date=date(2026, 7, 1),
                status="OPEN",
                created_at=seeded_at,
                updated_at=seeded_at,
            ),
            MembershipBillingReferenceOrmModel(
                id="c7000000-0000-0000-0000-000000000003",
                membership_id="b7000000-0000-0000-0000-000000000003",
                external_invoice_id="seed-external-paid",
                external_invoice_reference="seed-local-paid",
                due_date=date(2026, 5, 1),
                status="PAID",
                created_at=seeded_at,
                updated_at=updated_paid_at,
            ),
            MembershipBillingReferenceOrmModel(
                id="c7000000-0000-0000-0000-000000000004",
                membership_id="b7000000-0000-0000-0000-000000000004",
                external_invoice_id="seed-external-suspended",
                external_invoice_reference="seed-local-suspended",
                due_date=date(2026, 5, 1),
                status="OPEN",
                created_at=seeded_at,
                updated_at=seeded_at,
            ),
            MembershipBillingReferenceOrmModel(
                id="c7000000-0000-0000-0000-000000000005",
                membership_id="b7000000-0000-0000-0000-000000000005",
                external_invoice_id="seed-external-cancelled",
                external_invoice_reference="seed-local-cancelled",
                due_date=date(2026, 5, 1),
                status="OPEN",
                created_at=seeded_at,
                updated_at=seeded_at,
            ),
            MembershipBillingReferenceOrmModel(
                id="c7000000-0000-0000-0000-000000000006",
                membership_id="b7000000-0000-0000-0000-000000000006",
                external_invoice_id="seed-external-paused",
                external_invoice_reference="seed-local-paused",
                due_date=date(2026, 7, 1),
                status="OPEN",
                created_at=seeded_at,
                updated_at=seeded_at,
            ),
        ]:
            session.merge(billing_reference)

        session.commit()
    finally:
        session.close()


def ensure_workshop_schema() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    if "memberships" in existing_tables:
        membership_columns = {
            column["name"] for column in inspector.get_columns("memberships")
        }
        if "reason" not in membership_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE memberships ADD COLUMN reason VARCHAR(100)"))
        missing_membership_columns = {
            "pause_start_date": "DATE",
            "pause_end_date": "DATE",
            "pause_reason": "VARCHAR(100)",
            "cancelled_at": "TIMESTAMP",
            "cancellation_reason": "VARCHAR(100)",
        }
        for column_name, column_type in missing_membership_columns.items():
            if column_name not in membership_columns:
                with engine.begin() as connection:
                    connection.execute(
                        text(f"ALTER TABLE memberships ADD COLUMN {column_name} {column_type}")
                    )


def init_db() -> None:
    from workshop_api.fitness.layered.infrastructure.customer_entity import CustomerOrmModel
    from workshop_api.fitness.layered.infrastructure.membership_entity import (
        MembershipBillingReferenceOrmModel,
        MembershipOrmModel,
    )
    from workshop_api.fitness.layered.infrastructure.plan_entity import PlanOrmModel

    try:
        Base.metadata.create_all(
            bind=engine,
            tables=[
                CustomerOrmModel.__table__,
                PlanOrmModel.__table__,
                MembershipOrmModel.__table__,
                MembershipBillingReferenceOrmModel.__table__,
            ],
        )
        ensure_workshop_schema()
        seed_demo_data()
    except OperationalError as error:
        if "readonly" in str(error).lower():
            return
        raise
