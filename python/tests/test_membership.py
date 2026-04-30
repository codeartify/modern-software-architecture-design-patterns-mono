from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from workshop_api.external_invoice_provider.invoice_provider_controller import (
    store as external_invoice_store,
)
from workshop_api.fitness import database
from workshop_api.fitness.database import Base
from workshop_api.fitness.managing_customers.shared.customer_entity import CustomerOrmModel
from workshop_api.fitness.managing_memberships.shared.in_memory_email_service import email_service
from workshop_api.fitness.managing_memberships.shared.membership_entity import (
    MembershipBillingReferenceOrmModel,
    MembershipOrmModel,
)
from workshop_api.fitness.managing_plans.shared.plan_entity import PlanOrmModel
from workshop_api.main import app

MEMBERSHIPS_BASE_PATH = "/api/memberships"


def test_membership_activate_membership_creates_membership_invoice_and_email(
    tmp_path: Path, monkeypatch
) -> None:
    test_sessionmaker = _membership_test_sessionmaker(
        tmp_path,
        "membership-membership-test.db",
        [
            CustomerOrmModel.__table__,
            PlanOrmModel.__table__,
            MembershipOrmModel.__table__,
            MembershipBillingReferenceOrmModel.__table__,
        ],
    )
    setup_session = test_sessionmaker()
    setup_session.add(
        CustomerOrmModel(
            id="11111111-1111-1111-1111-111111111111",
            name="Alice Active",
            date_of_birth=date(1986, 8, 13),
            email_address="alice.active@example.com",
        )
    )
    setup_session.add(
        PlanOrmModel(
            id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
            title="Premium 12 Months",
            description="Twelve months for regular training",
            duration_in_months=12,
            price=Decimal("999.00"),
        )
    )
    setup_session.commit()
    setup_session.close()

    client = _membership_test_client(test_sessionmaker, monkeypatch)

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/activate",
        json={
            "customerId": "11111111-1111-1111-1111-111111111111",
            "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
            "signedByCustodian": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ACTIVE"
    assert response.json()["planPrice"] == 999
    assert response.json()["planDuration"] == 12
    assert response.json()["startDate"] is not None
    assert "reason" not in response.json()
    assert len(external_invoice_store.find_all()) == 1
    assert (
        external_invoice_store.find_all()[0].contract_reference
        == response.json()["membershipId"]
    )

    verification_session = test_sessionmaker()
    assert verification_session.query(MembershipOrmModel).count() == 1
    assert verification_session.query(MembershipBillingReferenceOrmModel).count() == 1
    stored_billing_reference = verification_session.query(
        MembershipBillingReferenceOrmModel
    ).one()
    assert stored_billing_reference.membership_id == response.json()["membershipId"]
    assert stored_billing_reference.external_invoice_id == response.json()["externalInvoiceId"]
    assert stored_billing_reference.external_invoice_reference == response.json()["invoiceId"]
    assert str(stored_billing_reference.due_date) == response.json()["invoiceDueDate"]
    assert stored_billing_reference.status == "OPEN"
    verification_session.close()
    assert len(email_service.sent_emails()) == 1
    assert "billing@codeartify.com" in email_service.sent_emails()[0]
    assert response.json()["invoiceId"] in email_service.sent_emails()[0]

    app.dependency_overrides.clear()


def test_membership_activate_membership_rejects_minor_without_custodian_signature(
    tmp_path: Path, monkeypatch
) -> None:
    test_sessionmaker = _membership_test_sessionmaker(
        tmp_path,
        "membership-membership-minor-test.db",
        [
            CustomerOrmModel.__table__,
            PlanOrmModel.__table__,
            MembershipOrmModel.__table__,
            MembershipBillingReferenceOrmModel.__table__,
        ],
    )
    setup_session = test_sessionmaker()
    setup_session.add(
        CustomerOrmModel(
            id="44444444-4444-4444-4444-444444444444",
            name="Mila Minor",
            date_of_birth=date(2010, 9, 14),
            email_address="mila.minor@example.com",
        )
    )
    setup_session.add(
        PlanOrmModel(
            id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
            title="Premium 12 Months",
            description="Twelve months for regular training",
            duration_in_months=12,
            price=Decimal("999.00"),
        )
    )
    setup_session.commit()
    setup_session.close()

    client = _membership_test_client(test_sessionmaker, monkeypatch)

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/activate",
        json={
            "customerId": "44444444-4444-4444-4444-444444444444",
            "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
        },
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Customers younger than 18 require signedByCustodian=true"
    assert external_invoice_store.find_all() == []
    assert email_service.sent_emails() == []

    verification_session = test_sessionmaker()
    assert verification_session.query(MembershipOrmModel).count() == 0
    assert verification_session.query(MembershipBillingReferenceOrmModel).count() == 0
    verification_session.close()
    app.dependency_overrides.clear()


def test_membership_list_memberships_returns_all_memberships(tmp_path: Path) -> None:
    test_sessionmaker = _membership_test_sessionmaker(
        tmp_path,
        "membership-membership-list-test.db",
        [MembershipOrmModel.__table__],
    )
    setup_session = test_sessionmaker()
    setup_session.add_all(
        [
            MembershipOrmModel(
                id="b7000000-0000-0000-0000-000000000001",
                customer_id="11111111-1111-1111-1111-111111111111",
                plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                plan_price=999,
                plan_duration=12,
                status="ACTIVE",
                reason=None,
                start_date=date(2026, 1, 1),
                end_date=date(2027, 1, 1),
            ),
            MembershipOrmModel(
                id="b7000000-0000-0000-0000-000000000002",
                customer_id="22222222-2222-2222-2222-222222222222",
                plan_id="aaaaaa24-aaaa-aaaa-aaaa-aaaaaaaaaa24",
                plan_price=1699,
                plan_duration=24,
                status="SUSPENDED",
                reason="NON_PAYMENT",
                start_date=date(2026, 1, 1),
                end_date=date(2028, 1, 1),
            ),
        ]
    )
    setup_session.commit()
    setup_session.close()

    app.dependency_overrides[database.get_db_session] = _get_test_db(test_sessionmaker)
    client = TestClient(app)

    response = client.get(MEMBERSHIPS_BASE_PATH)

    assert response.status_code == 200
    assert {membership["membershipId"] for membership in response.json()} == {
        "b7000000-0000-0000-0000-000000000001",
        "b7000000-0000-0000-0000-000000000002",
    }
    assert {membership["status"] for membership in response.json()} == {"ACTIVE", "SUSPENDED"}

    app.dependency_overrides.clear()


def test_membership_get_membership_returns_membership_by_id(tmp_path: Path) -> None:
    test_sessionmaker = _membership_test_sessionmaker(
        tmp_path,
        "membership-membership-get-test.db",
        [MembershipOrmModel.__table__],
    )
    setup_session = test_sessionmaker()
    setup_session.add(
        MembershipOrmModel(
            id="b7000000-0000-0000-0000-000000000003",
            customer_id="33333333-3333-3333-3333-333333333333",
            plan_id="aaaaaaa6-aaaa-aaaa-aaaa-aaaaaaaaaaa6",
            plan_price=599,
            plan_duration=6,
            status="ACTIVE",
            reason=None,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 8, 1),
        )
    )
    setup_session.commit()
    setup_session.close()

    app.dependency_overrides[database.get_db_session] = _get_test_db(test_sessionmaker)
    client = TestClient(app)

    response = client.get(
        f"{MEMBERSHIPS_BASE_PATH}/b7000000-0000-0000-0000-000000000003"
    )

    assert response.status_code == 200
    assert response.json()["membershipId"] == "b7000000-0000-0000-0000-000000000003"
    assert response.json()["customerId"] == "33333333-3333-3333-3333-333333333333"
    assert response.json()["planId"] == "aaaaaaa6-aaaa-aaaa-aaaa-aaaaaaaaaaa6"
    assert response.json()["planPrice"] == 599
    assert response.json()["planDuration"] == 6
    assert response.json()["status"] == "ACTIVE"
    assert response.json()["reason"] is None
    assert response.json()["startDate"] == "2026-02-01"
    assert response.json()["endDate"] == "2026-08-01"

    app.dependency_overrides.clear()


def _membership_test_sessionmaker(tmp_path: Path, database_name: str, tables):
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
    Base.metadata.create_all(bind=test_engine, tables=tables)
    return test_sessionmaker


def _membership_test_client(test_sessionmaker, monkeypatch) -> TestClient:
    monkeypatch.setenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://testserver")
    monkeypatch.setenv("WORKSHOP_BILLING_SENDER_EMAIL_ADDRESS", "billing@codeartify.com")
    app.dependency_overrides[database.get_db_session] = _get_test_db(test_sessionmaker)
    external_invoice_store.clear()
    email_service.clear()
    return TestClient(app)


def _get_test_db(test_sessionmaker):
    def get_test_db():
        override_session = test_sessionmaker()
        try:
            yield override_session
        finally:
            override_session.close()

    return get_test_db
