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
from workshop_api.fitness.external_invoice_provider.schemas import (
    ExternalInvoiceProviderUpsertRequest,
)
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
    assert (
        external_invoice_store.list_invoices()[0].contract_reference
        == response.json()["membershipId"]
    )
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


def test_e00_suspend_membership_changes_status_without_extending_runtime(
    tmp_path: Path, monkeypatch
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'e00-membership-suspend-test.db'}",
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
    app.dependency_overrides[database.get_db_session] = get_test_db
    external_invoice_store.clear()
    email_service.clear()
    client = TestClient(app)

    activated_membership = client.post(
        "/api/e00/memberships/activate",
        json={
            "customerId": "11111111-1111-1111-1111-111111111111",
            "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
            "signedByCustodian": False,
        },
    )

    suspended_membership = client.post(
        f"/api/e00/memberships/{activated_membership.json()['membershipId']}/suspend"
    )

    assert suspended_membership.status_code == 200
    assert suspended_membership.json()["status"] == "SUSPENDED"
    assert suspended_membership.json()["startDate"] == activated_membership.json()["startDate"]
    assert suspended_membership.json()["endDate"] == activated_membership.json()["endDate"]

    app.dependency_overrides.clear()


def test_e00_suspend_membership_rejects_membership_that_is_not_active(
    tmp_path: Path, monkeypatch
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'e00-membership-suspend-reject-test.db'}",
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
    app.dependency_overrides[database.get_db_session] = get_test_db
    external_invoice_store.clear()
    email_service.clear()
    client = TestClient(app)

    activated_membership = client.post(
        "/api/e00/memberships/activate",
        json={
            "customerId": "11111111-1111-1111-1111-111111111111",
            "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
            "signedByCustodian": False,
        },
    )

    client.post(f"/api/e00/memberships/{activated_membership.json()['membershipId']}/suspend")
    rejected_suspend = client.post(
        f"/api/e00/memberships/{activated_membership.json()['membershipId']}/suspend"
    )

    assert rejected_suspend.status_code == 400
    assert "must be ACTIVE to suspend" in rejected_suspend.json()["detail"]

    app.dependency_overrides.clear()


def test_e00_suspend_overdue_memberships_suspends_only_active_overdue_memberships(
    tmp_path: Path, monkeypatch
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'e00-membership-overdue-test.db'}",
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
    active_overdue_membership = E00MembershipOrmModel(
        id="membership-active-overdue",
        customer_id="11111111-1111-1111-1111-111111111111",
        plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
        plan_price=999,
        plan_duration=12,
        status="ACTIVE",
        reason=None,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
    )
    active_not_overdue_membership = E00MembershipOrmModel(
        id="membership-active-current",
        customer_id="11111111-1111-1111-1111-111111111111",
        plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
        plan_price=999,
        plan_duration=12,
        status="ACTIVE",
        reason=None,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
    )
    suspended_membership = E00MembershipOrmModel(
        id="membership-suspended",
        customer_id="11111111-1111-1111-1111-111111111111",
        plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
        plan_price=999,
        plan_duration=12,
        status="SUSPENDED",
        reason=None,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
    )
    cancelled_membership = E00MembershipOrmModel(
        id="membership-cancelled",
        customer_id="11111111-1111-1111-1111-111111111111",
        plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
        plan_price=999,
        plan_duration=12,
        status="CANCELLED",
        reason=None,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
    )
    setup_session.add_all(
        [
            active_overdue_membership,
            active_not_overdue_membership,
            suspended_membership,
            cancelled_membership,
        ]
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
    external_invoice_store.save(
        "external-overdue-1",
        ExternalInvoiceProviderUpsertRequest(
            customerReference="11111111-1111-1111-1111-111111111111",
            contractReference="membership-active-overdue",
            amountInCents=999,
            currency="CHF",
            dueDate="2026-04-01",
            status="OPEN",
            description="Overdue invoice",
            externalCorrelationId="corr-overdue-1",
            metadata={"exercise": "e00"},
        ),
    )
    external_invoice_store.save(
        "external-future-1",
        ExternalInvoiceProviderUpsertRequest(
            customerReference="11111111-1111-1111-1111-111111111111",
            contractReference="membership-active-current",
            amountInCents=999,
            currency="CHF",
            dueDate="2026-05-10",
            status="OPEN",
            description="Current invoice",
            externalCorrelationId="corr-future-1",
            metadata={"exercise": "e00"},
        ),
    )
    external_invoice_store.save(
        "external-cancelled-1",
        ExternalInvoiceProviderUpsertRequest(
            customerReference="11111111-1111-1111-1111-111111111111",
            contractReference="membership-cancelled",
            amountInCents=999,
            currency="CHF",
            dueDate="2026-04-01",
            status="OPEN",
            description="Cancelled membership invoice",
            externalCorrelationId="corr-cancelled-1",
            metadata={"exercise": "e00"},
        ),
    )
    external_invoice_store.save(
        "external-paid-1",
        ExternalInvoiceProviderUpsertRequest(
            customerReference="11111111-1111-1111-1111-111111111111",
            contractReference="membership-suspended",
            amountInCents=999,
            currency="CHF",
            dueDate="2026-04-01",
            status="PAID",
            description="Paid invoice",
            externalCorrelationId="corr-paid-1",
            metadata={"exercise": "e00"},
        ),
    )
    client = TestClient(app)

    response = client.post(
        "/api/e00/memberships/suspend-overdue",
        json={"checkedAt": "2026-04-27T10:00:00Z"},
    )

    assert response.status_code == 200
    assert response.json()["checkedMemberships"] == 2
    assert response.json()["suspendedMembershipIds"] == ["membership-active-overdue"]

    verification_session = test_sessionmaker()
    assert (
        verification_session.get(
            E00MembershipOrmModel, "membership-active-overdue"
        ).status
        == "SUSPENDED"
    )
    assert (
        verification_session.get(E00MembershipOrmModel, "membership-active-overdue").reason
        == "NON_PAYMENT"
    )
    assert (
        verification_session.get(
            E00MembershipOrmModel, "membership-active-current"
        ).status
        == "ACTIVE"
    )
    assert (
        verification_session.get(E00MembershipOrmModel, "membership-suspended").status
        == "SUSPENDED"
    )
    assert (
        verification_session.get(E00MembershipOrmModel, "membership-cancelled").status
        == "CANCELLED"
    )
    verification_session.close()

    second_response = client.post(
        "/api/e00/memberships/suspend-overdue",
        json={"checkedAt": "2026-04-27T10:00:00Z"},
    )

    assert second_response.status_code == 200
    assert second_response.json()["checkedMemberships"] == 1
    assert second_response.json()["suspendedMembershipIds"] == []

    app.dependency_overrides.clear()
