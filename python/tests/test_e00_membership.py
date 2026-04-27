from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from workshop_api.fitness.customer import database
from workshop_api.fitness.customer.database import Base
from workshop_api.fitness.customer.models import CustomerOrmModel
from workshop_api.fitness.email.service import email_service
from workshop_api.fitness.external_invoice_provider.router import store as external_invoice_store
from workshop_api.fitness.membership.exercise00_mixed.models import E00MembershipOrmModel
from workshop_api.fitness.plan.models import PlanOrmModel
from workshop_api.main import app


def test_e00_activate_membership_creates_membership_invoice_and_email(
    tmp_path: Path, monkeypatch
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'e00-membership-test.db'}",
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
            E00MembershipOrmModel.__table__,
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

    def get_test_db():
        override_session = test_sessionmaker()
        try:
            yield override_session
        finally:
            override_session.close()

    monkeypatch.setenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://testserver")
    monkeypatch.setenv("WORKSHOP_BILLING_SENDER_EMAIL_ADDRESS", "billing@codeartify.com")
    app.dependency_overrides[database.get_db_session] = get_test_db
    external_invoice_store.clear()
    email_service.clear()
    client = TestClient(app)

    response = client.post(
        "/api/e00/memberships/activate",
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
    assert len(external_invoice_store.list_invoices()) == 1
    assert external_invoice_store.list_invoices()[0].contract_reference == response.json()["membershipId"]
    assert len(email_service.sent_emails()) == 1
    assert "billing@codeartify.com" in email_service.sent_emails()[0]
    assert response.json()["invoiceId"] in email_service.sent_emails()[0]

    app.dependency_overrides.clear()


def test_e00_activate_membership_rejects_minor_without_custodian_signature(
    tmp_path: Path, monkeypatch
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'e00-membership-minor-test.db'}",
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
            E00MembershipOrmModel.__table__,
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

    def get_test_db():
        override_session = test_sessionmaker()
        try:
            yield override_session
        finally:
            override_session.close()

    monkeypatch.setenv("WORKSHOP_EXTERNAL_INVOICE_PROVIDER_BASE_URL", "http://testserver")
    app.dependency_overrides[database.get_db_session] = get_test_db
    external_invoice_store.clear()
    email_service.clear()
    client = TestClient(app)

    response = client.post(
        "/api/e00/memberships/activate",
        json={
            "customerId": "44444444-4444-4444-4444-444444444444",
            "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Customers younger than 18 require signedByCustodian=true"
    assert external_invoice_store.list_invoices() == []
    assert email_service.sent_emails() == []

    app.dependency_overrides.clear()
