from datetime import UTC, date, datetime
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from workshop_api.external_invoice_provider.invoice_provider_controller import (
    store as external_invoice_store,
)
from workshop_api.fitness import database
from workshop_api.fitness.database import Base
from workshop_api.fitness.shared.membership_entity import (
    MembershipBillingReferenceOrmModel,
    MembershipOrmModel,
)
from workshop_api.main import app


def test_membership_pause_and_resume_flow(tmp_path: Path) -> None:
    test_sessionmaker = _membership_lifecycle_sessionmaker(tmp_path, "pause-resume.db")
    setup_session = test_sessionmaker()
    setup_session.add(_membership("b7000000-0000-0000-0000-000000000010", status="ACTIVE"))
    setup_session.commit()
    setup_session.close()

    app.dependency_overrides[database.get_db_session] = _get_test_db(test_sessionmaker)
    client = TestClient(app)

    pause_response = client.post(
        "/api/memberships/b7000000-0000-0000-0000-000000000010/pause",
        json={
            "pauseStartDate": "2026-06-01",
            "pauseEndDate": "2026-06-14",
            "reason": "Holiday",
        },
    )

    assert pause_response.status_code == 200
    assert pause_response.json()["previousStatus"] == "ACTIVE"
    assert pause_response.json()["newStatus"] == "PAUSED"
    assert pause_response.json()["previousEndDate"] == "2026-12-31"
    assert pause_response.json()["newEndDate"] == "2027-01-14"

    resume_response = client.post(
        "/api/memberships/b7000000-0000-0000-0000-000000000010/resume",
        json={
            "resumedAt": "2026-06-10T10:00:00Z",
            "reason": "Back early",
        },
    )

    assert resume_response.status_code == 200
    assert resume_response.json()["previousStatus"] == "PAUSED"
    assert resume_response.json()["newStatus"] == "ACTIVE"
    assert resume_response.json()["previousPauseStartDate"] == "2026-06-01"
    assert resume_response.json()["previousPauseEndDate"] == "2026-06-14"
    assert resume_response.json()["endDate"] == "2027-01-14"

    app.dependency_overrides.clear()


def test_membership_cancel_flow(tmp_path: Path) -> None:
    test_sessionmaker = _membership_lifecycle_sessionmaker(tmp_path, "cancel.db")
    setup_session = test_sessionmaker()
    setup_session.add(_membership("b7000000-0000-0000-0000-000000000011", status="ACTIVE"))
    setup_session.commit()
    setup_session.close()

    app.dependency_overrides[database.get_db_session] = _get_test_db(test_sessionmaker)
    client = TestClient(app)

    response = client.post(
        "/api/memberships/b7000000-0000-0000-0000-000000000011/cancel",
        json={
            "cancelledAt": "2026-04-30T10:00:00Z",
            "reason": "Moving away",
        },
    )

    assert response.status_code == 200
    assert response.json()["previousStatus"] == "ACTIVE"
    assert response.json()["newStatus"] == "CANCELLED"
    assert response.json()["reason"] == "Moving away"
    assert response.json()["message"] == "Membership cancelled"

    app.dependency_overrides.clear()


def test_membership_suspend_overdue_and_payment_received_reactivates(
    tmp_path: Path,
) -> None:
    test_sessionmaker = _membership_lifecycle_sessionmaker(tmp_path, "payment.db")
    setup_session = test_sessionmaker()
    setup_session.add(_membership("b7000000-0000-0000-0000-000000000012", status="ACTIVE"))
    setup_session.add(
        MembershipBillingReferenceOrmModel(
            id="c7000000-0000-0000-0000-000000000012",
            membership_id="b7000000-0000-0000-0000-000000000012",
            external_invoice_id="external-overdue",
            external_invoice_reference="local-overdue",
            due_date=date(2026, 1, 1),
            status="OPEN",
            created_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
        )
    )
    setup_session.commit()
    setup_session.close()

    app.dependency_overrides[database.get_db_session] = _get_test_db(test_sessionmaker)
    client = TestClient(app)

    suspend_response = client.post(
        "/api/memberships/suspend-overdue",
        json={"checkedAt": "2026-04-30T10:00:00Z"},
    )

    assert suspend_response.status_code == 200
    assert suspend_response.json()["checkedMemberships"] == 1
    assert suspend_response.json()["suspendedMembershipIds"] == [
        "b7000000-0000-0000-0000-000000000012"
    ]

    payment_response = client.post(
        "/api/memberships/payment-received",
        json={
            "externalInvoiceId": "external-overdue",
            "paidAt": "2026-04-30T10:00:00Z",
        },
    )

    assert payment_response.status_code == 200
    assert payment_response.json()["previousMembershipStatus"] == "SUSPENDED"
    assert payment_response.json()["newMembershipStatus"] == "ACTIVE"
    assert payment_response.json()["reactivated"] is True
    assert payment_response.json()["message"] == "Payment recorded; membership reactivated"

    verification_session = test_sessionmaker()
    membership = verification_session.get(
        MembershipOrmModel,
        "b7000000-0000-0000-0000-000000000012",
    )
    billing_reference = verification_session.get(
        MembershipBillingReferenceOrmModel,
        "c7000000-0000-0000-0000-000000000012",
    )
    assert membership.status == "ACTIVE"
    assert membership.reason is None
    assert billing_reference.status == "PAID"
    verification_session.close()
    app.dependency_overrides.clear()


def test_membership_billable_extend_creates_invoice(tmp_path: Path, monkeypatch) -> None:
    test_sessionmaker = _membership_lifecycle_sessionmaker(tmp_path, "extend.db")
    setup_session = test_sessionmaker()
    setup_session.add(_membership("b7000000-0000-0000-0000-000000000013", status="ACTIVE"))
    setup_session.commit()
    setup_session.close()

    monkeypatch.setenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://testserver")
    external_invoice_store.clear()
    app.dependency_overrides[database.get_db_session] = _get_test_db(test_sessionmaker)
    client = TestClient(app)

    response = client.post(
        "/api/memberships/b7000000-0000-0000-0000-000000000013/extend",
        json={
            "additionalMonths": 1,
            "additionalDays": 2,
            "billable": True,
            "price": 12900,
            "reason": "Manual extension",
        },
    )

    assert response.status_code == 200
    assert response.json()["previousEndDate"] == "2026-12-31"
    assert response.json()["newEndDate"] == "2027-02-02"
    assert response.json()["billable"] is True
    assert response.json()["billingReferenceId"] is not None
    assert response.json()["externalInvoiceId"] is not None
    assert response.json()["message"] == "Membership extended and invoice created"
    assert len(external_invoice_store.find_all()) == 1
    assert external_invoice_store.find_all()[0].amount_in_cents == 12900

    app.dependency_overrides.clear()


def _membership_lifecycle_sessionmaker(tmp_path: Path, database_name: str):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / database_name}",
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
            MembershipOrmModel.__table__,
            MembershipBillingReferenceOrmModel.__table__,
        ],
    )
    return test_sessionmaker


def _get_test_db(test_sessionmaker):
    def get_test_db():
        session = test_sessionmaker()
        try:
            yield session
        finally:
            session.close()

    return get_test_db


def _membership(membership_id: str, status: str) -> MembershipOrmModel:
    return MembershipOrmModel(
        id=membership_id,
        customer_id="11111111-1111-1111-1111-111111111111",
        plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
        plan_price=999,
        plan_duration=12,
        status=status,
        reason=None,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )
