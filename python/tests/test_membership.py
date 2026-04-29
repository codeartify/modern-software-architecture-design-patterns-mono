from datetime import date, datetime
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
from workshop_api.fitness.membership.models import (
    MembershipBillingReferenceOrmModel,
    MembershipOrmModel,
)
from workshop_api.fitness.plan.models import PlanOrmModel
from workshop_api.main import app

MEMBERSHIPS_BASE_PATH = "/api/memberships"


def test_membership_activate_membership_creates_membership_invoice_and_email(
    tmp_path: Path, monkeypatch
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-membership-test.db'}",
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
    assert len(external_invoice_store.list_invoices()) == 1
    assert (
        external_invoice_store.list_invoices()[0].contract_reference
        == response.json()["membershipId"]
    )
    verification_session = test_sessionmaker()
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
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-membership-minor-test.db'}",
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
        f"{MEMBERSHIPS_BASE_PATH}/activate",
        json={
            "customerId": "44444444-4444-4444-4444-444444444444",
            "planId": "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "status": 400,
        "error": "Bad Request",
        "message": "Customers younger than 18 require signedByCustodian=true",
        "path": f"{MEMBERSHIPS_BASE_PATH}/activate",
    }
    assert external_invoice_store.list_invoices() == []
    assert email_service.sent_emails() == []

    app.dependency_overrides.clear()


def test_membership_get_membership_rejects_malformed_membership_id() -> None:
    client = TestClient(app)

    response = client.get(f"{MEMBERSHIPS_BASE_PATH}/not-a-uuid")

    assert response.status_code == 400
    assert response.json() == {
        "status": 400,
        "error": "Bad Request",
        "message": "Invalid value for 'membershipId': not-a-uuid",
        "path": f"{MEMBERSHIPS_BASE_PATH}/not-a-uuid",
    }


def test_membership_list_memberships_returns_all_memberships(tmp_path: Path) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-membership-list-test.db'}",
        connect_args={"check_same_thread": False},
    )
    test_sessionmaker = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=test_engine, tables=[MembershipOrmModel.__table__])

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

    def get_test_db():
        override_session = test_sessionmaker()
        try:
            yield override_session
        finally:
            override_session.close()

    app.dependency_overrides[database.get_db_session] = get_test_db
    client = TestClient(app)

    response = client.get(MEMBERSHIPS_BASE_PATH)

    assert response.status_code == 200
    assert response.json()[0]["membershipId"] == "b7000000-0000-0000-0000-000000000001"
    assert response.json()[0]["customerId"] == "11111111-1111-1111-1111-111111111111"
    assert response.json()[0]["planId"] == "aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12"
    assert response.json()[0]["planPrice"] == 999
    assert response.json()[0]["planDuration"] == 12
    assert response.json()[0]["status"] == "ACTIVE"
    assert response.json()[0]["reason"] is None
    assert response.json()[0]["startDate"] == "2026-01-01"
    assert response.json()[0]["endDate"] == "2027-01-01"
    assert response.json()[1]["membershipId"] == "b7000000-0000-0000-0000-000000000002"
    assert response.json()[1]["customerId"] == "22222222-2222-2222-2222-222222222222"
    assert response.json()[1]["planId"] == "aaaaaa24-aaaa-aaaa-aaaa-aaaaaaaaaa24"
    assert response.json()[1]["planPrice"] == 1699
    assert response.json()[1]["planDuration"] == 24
    assert response.json()[1]["status"] == "SUSPENDED"
    assert response.json()[1]["reason"] == "NON_PAYMENT"
    assert response.json()[1]["startDate"] == "2026-01-01"
    assert response.json()[1]["endDate"] == "2028-01-01"

    app.dependency_overrides.clear()


def test_membership_get_membership_returns_membership_by_id(tmp_path: Path) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-membership-get-test.db'}",
        connect_args={"check_same_thread": False},
    )
    test_sessionmaker = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=test_engine, tables=[MembershipOrmModel.__table__])

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

    def get_test_db():
        override_session = test_sessionmaker()
        try:
            yield override_session
        finally:
            override_session.close()

    app.dependency_overrides[database.get_db_session] = get_test_db
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


def test_membership_suspend_overdue_memberships_suspends_only_active_overdue_memberships(
    tmp_path: Path,
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-membership-overdue-test.db'}",
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

    setup_session = test_sessionmaker()
    active_overdue_membership = MembershipOrmModel(
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
    active_not_overdue_membership = MembershipOrmModel(
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
    active_paid_membership = MembershipOrmModel(
        id="membership-active-paid",
        customer_id="11111111-1111-1111-1111-111111111111",
        plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
        plan_price=999,
        plan_duration=12,
        status="ACTIVE",
        reason=None,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 1, 1),
    )
    suspended_membership = MembershipOrmModel(
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
    cancelled_membership = MembershipOrmModel(
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
            active_paid_membership,
            suspended_membership,
            cancelled_membership,
            MembershipBillingReferenceOrmModel(
                id="billing-active-overdue",
                membership_id="membership-active-overdue",
                external_invoice_id="external-overdue-1",
                external_invoice_reference="corr-overdue-1",
                due_date=date(2026, 4, 1),
                status="OPEN",
                created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
                updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            ),
            MembershipBillingReferenceOrmModel(
                id="billing-active-current",
                membership_id="membership-active-current",
                external_invoice_id="external-future-1",
                external_invoice_reference="corr-future-1",
                due_date=date(2026, 5, 10),
                status="OPEN",
                created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
                updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            ),
            MembershipBillingReferenceOrmModel(
                id="billing-active-paid",
                membership_id="membership-active-paid",
                external_invoice_id="external-paid-1",
                external_invoice_reference="corr-paid-1",
                due_date=date(2026, 4, 1),
                status="PAID",
                created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
                updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            ),
            MembershipBillingReferenceOrmModel(
                id="billing-suspended",
                membership_id="membership-suspended",
                external_invoice_id="external-suspended-1",
                external_invoice_reference="corr-suspended-1",
                due_date=date(2026, 4, 1),
                status="OPEN",
                created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
                updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            ),
            MembershipBillingReferenceOrmModel(
                id="billing-cancelled",
                membership_id="membership-cancelled",
                external_invoice_id="external-cancelled-1",
                external_invoice_reference="corr-cancelled-1",
                due_date=date(2026, 4, 1),
                status="OPEN",
                created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
                updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            ),
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

    app.dependency_overrides[database.get_db_session] = get_test_db
    client = TestClient(app)

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/suspend-overdue",
        json={"checkedAt": "2026-04-27T10:00:00Z"},
    )

    assert response.status_code == 200
    assert response.json()["checkedMemberships"] == 3
    assert response.json()["suspendedMembershipIds"] == ["membership-active-overdue"]

    verification_session = test_sessionmaker()
    assert (
        verification_session.get(
            MembershipOrmModel, "membership-active-overdue"
        ).status
        == "SUSPENDED"
    )
    assert (
        verification_session.get(MembershipOrmModel, "membership-active-overdue").reason
        == "NON_PAYMENT"
    )
    assert (
        verification_session.get(
            MembershipOrmModel, "membership-active-current"
        ).status
        == "ACTIVE"
    )
    assert (
        verification_session.get(MembershipOrmModel, "membership-active-paid").status
        == "ACTIVE"
    )
    assert (
        verification_session.get(MembershipOrmModel, "membership-suspended").status
        == "SUSPENDED"
    )
    assert (
        verification_session.get(MembershipOrmModel, "membership-cancelled").status
        == "CANCELLED"
    )
    verification_session.close()

    second_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/suspend-overdue",
        json={"checkedAt": "2026-04-27T10:00:00Z"},
    )

    assert second_response.status_code == 200
    assert second_response.json()["checkedMemberships"] == 2
    assert second_response.json()["suspendedMembershipIds"] == []

    app.dependency_overrides.clear()


def test_membership_payment_received_for_active_membership_marks_billing_reference_paid(
    tmp_path: Path,
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-payment-active-test.db'}",
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

    setup_session = test_sessionmaker()
    setup_session.add(
        MembershipOrmModel(
            id="membership-active",
            customer_id="11111111-1111-1111-1111-111111111111",
            plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
            plan_price=999,
            plan_duration=12,
            status="ACTIVE",
            reason=None,
            start_date=date(2026, 1, 1),
            end_date=date(2027, 1, 1),
        )
    )
    setup_session.add(
        MembershipBillingReferenceOrmModel(
            id="billing-active",
            membership_id="membership-active",
            external_invoice_id="external-001",
            external_invoice_reference="local-001",
            due_date=date(2026, 2, 1),
            status="OPEN",
            created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
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

    app.dependency_overrides[database.get_db_session] = get_test_db
    client = TestClient(app)

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/payment-received",
        json={
            "externalInvoiceId": "external-001",
            "paidAt": "2026-01-15T10:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json()["membershipId"] == "membership-active"
    assert response.json()["billingReferenceId"] == "billing-active"
    assert response.json()["previousMembershipStatus"] == "ACTIVE"
    assert response.json()["newMembershipStatus"] == "ACTIVE"
    assert response.json()["reactivated"] is False
    assert response.json()["message"] == "Payment recorded; membership status unchanged"

    verification_session = test_sessionmaker()
    billing_reference = verification_session.get(
        MembershipBillingReferenceOrmModel, "billing-active"
    )
    membership = verification_session.get(MembershipOrmModel, "membership-active")
    assert billing_reference.status == "PAID"
    assert membership.status == "ACTIVE"
    verification_session.close()
    app.dependency_overrides.clear()


def test_membership_payment_received_reactivates_membership_suspended_for_non_payment_within_period(
    tmp_path: Path,
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-payment-reactivate-test.db'}",
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

    setup_session = test_sessionmaker()
    setup_session.add(
        MembershipOrmModel(
            id="membership-suspended-non-payment",
            customer_id="11111111-1111-1111-1111-111111111111",
            plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
            plan_price=999,
            plan_duration=12,
            status="SUSPENDED",
            reason="NON_PAYMENT",
            start_date=date(2026, 1, 1),
            end_date=date(2027, 1, 1),
        )
    )
    setup_session.add(
        MembershipBillingReferenceOrmModel(
            id="billing-reactivate",
            membership_id="membership-suspended-non-payment",
            external_invoice_id="external-002",
            external_invoice_reference="local-002",
            due_date=date(2026, 2, 1),
            status="OPEN",
            created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
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

    app.dependency_overrides[database.get_db_session] = get_test_db
    client = TestClient(app)

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/payment-received",
        json={
            "externalInvoiceReference": "local-002",
            "paidAt": "2026-02-15T10:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json()["previousMembershipStatus"] == "SUSPENDED"
    assert response.json()["newMembershipStatus"] == "ACTIVE"
    assert response.json()["reactivated"] is True
    assert response.json()["message"] == "Payment recorded; membership reactivated"

    verification_session = test_sessionmaker()
    membership = verification_session.get(
        MembershipOrmModel, "membership-suspended-non-payment"
    )
    assert membership.status == "ACTIVE"
    assert membership.reason is None
    verification_session.close()
    app.dependency_overrides.clear()


def test_membership_payment_received_keeps_suspended_membership_suspended_when_period_has_ended(
    tmp_path: Path,
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-payment-expired-test.db'}",
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

    setup_session = test_sessionmaker()
    setup_session.add(
        MembershipOrmModel(
            id="membership-expired",
            customer_id="11111111-1111-1111-1111-111111111111",
            plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
            plan_price=999,
            plan_duration=12,
            status="SUSPENDED",
            reason="NON_PAYMENT",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
        )
    )
    setup_session.add(
        MembershipBillingReferenceOrmModel(
            id="billing-expired",
            membership_id="membership-expired",
            external_invoice_id="external-003",
            external_invoice_reference="local-003",
            due_date=date(2025, 2, 1),
            status="OPEN",
            created_at=datetime.fromisoformat("2025-01-01T10:00:00+00:00"),
            updated_at=datetime.fromisoformat("2025-01-01T10:00:00+00:00"),
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

    app.dependency_overrides[database.get_db_session] = get_test_db
    client = TestClient(app)

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/payment-received",
        json={
            "externalInvoiceId": "external-003",
            "paidAt": "2026-01-10T10:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json()["newMembershipStatus"] == "SUSPENDED"
    assert response.json()["reactivated"] is False
    assert response.json()["message"] == "Payment recorded; membership status unchanged"
    app.dependency_overrides.clear()


def test_membership_payment_received_keeps_other_suspensions_and_cancellations_unchanged(
    tmp_path: Path,
) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-payment-conflicts-test.db'}",
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

    setup_session = test_sessionmaker()
    setup_session.add_all(
        [
            MembershipOrmModel(
                id="membership-manual-suspended",
                customer_id="11111111-1111-1111-1111-111111111111",
                plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                plan_price=999,
                plan_duration=12,
                status="SUSPENDED",
                reason="MANUAL_REVIEW",
                start_date=date(2026, 1, 1),
                end_date=date(2027, 1, 1),
            ),
            MembershipOrmModel(
                id="membership-cancelled",
                customer_id="11111111-1111-1111-1111-111111111111",
                plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
                plan_price=999,
                plan_duration=12,
                status="CANCELLED",
                reason=None,
                start_date=date(2026, 1, 1),
                end_date=date(2027, 1, 1),
            ),
        ]
    )
    setup_session.add_all(
        [
            MembershipBillingReferenceOrmModel(
                id="billing-manual-suspended",
                membership_id="membership-manual-suspended",
                external_invoice_id="external-004",
                external_invoice_reference="local-004",
                due_date=date(2026, 2, 1),
                status="OPEN",
                created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
                updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            ),
            MembershipBillingReferenceOrmModel(
                id="billing-cancelled",
                membership_id="membership-cancelled",
                external_invoice_id="external-005",
                external_invoice_reference="local-005",
                due_date=date(2026, 2, 1),
                status="OPEN",
                created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
                updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            ),
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

    app.dependency_overrides[database.get_db_session] = get_test_db
    client = TestClient(app)

    manual_suspended_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/payment-received",
        json={
            "externalInvoiceId": "external-004",
            "paidAt": "2026-02-10T10:00:00Z",
        },
    )
    cancelled_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/payment-received",
        json={
            "externalInvoiceId": "external-005",
            "paidAt": "2026-02-10T10:00:00Z",
        },
    )

    assert manual_suspended_response.status_code == 200
    assert manual_suspended_response.json()["newMembershipStatus"] == "SUSPENDED"
    assert (
        manual_suspended_response.json()["message"]
        == "Payment recorded; membership status unchanged"
    )
    assert cancelled_response.status_code == 200
    assert cancelled_response.json()["newMembershipStatus"] == "CANCELLED"
    assert (
        cancelled_response.json()["message"]
        == "Payment recorded; membership is cancelled and remains unchanged"
    )
    app.dependency_overrides.clear()


def test_membership_payment_received_is_idempotent_for_repeated_callbacks(tmp_path: Path) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-payment-idempotent-test.db'}",
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

    setup_session = test_sessionmaker()
    setup_session.add(
        MembershipOrmModel(
            id="membership-idempotent",
            customer_id="11111111-1111-1111-1111-111111111111",
            plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
            plan_price=999,
            plan_duration=12,
            status="ACTIVE",
            reason=None,
            start_date=date(2026, 1, 1),
            end_date=date(2027, 1, 1),
        )
    )
    setup_session.add(
        MembershipBillingReferenceOrmModel(
            id="billing-idempotent",
            membership_id="membership-idempotent",
            external_invoice_id="external-006",
            external_invoice_reference="local-006",
            due_date=date(2026, 2, 1),
            status="OPEN",
            created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
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

    app.dependency_overrides[database.get_db_session] = get_test_db
    client = TestClient(app)

    first_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/payment-received",
        json={
            "externalInvoiceId": "external-006",
            "paidAt": "2026-02-10T10:00:00Z",
        },
    )
    second_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/payment-received",
        json={
            "externalInvoiceId": "external-006",
            "paidAt": "2026-02-11T10:00:00Z",
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["membershipId"] == "membership-idempotent"
    assert second_response.json()["billingReferenceId"] == "billing-idempotent"
    assert second_response.json()["newMembershipStatus"] == "ACTIVE"
    assert second_response.json()["reactivated"] is False
    assert (
        first_response.json()["message"] == "Payment recorded; membership status unchanged"
    )
    assert (
        second_response.json()["message"]
        == "Payment was already recorded; membership status unchanged"
    )

    verification_session = test_sessionmaker()
    billing_reference = verification_session.get(
        MembershipBillingReferenceOrmModel, "billing-idempotent"
    )
    assert billing_reference.status == "PAID"
    verification_session.close()
    app.dependency_overrides.clear()


def _membership_lifecycle_test_client(tmp_path: Path, monkeypatch):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'membership-lifecycle-test.db'}",
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
    return test_sessionmaker, TestClient(app)


def _add_membership(
    test_sessionmaker,
    membership_id: str,
    status: str,
    end_date: date,
    reason: str | None = None,
) -> None:
    setup_session = test_sessionmaker()
    setup_session.add(
        MembershipOrmModel(
            id=membership_id,
            customer_id="11111111-1111-1111-1111-111111111111",
            plan_id="aaaaaa12-aaaa-aaaa-aaaa-aaaaaaaaaa12",
            plan_price=999,
            plan_duration=12,
            status=status,
            reason=reason,
            start_date=date(2026, 1, 1),
            end_date=end_date,
        )
    )
    setup_session.commit()
    setup_session.close()


def _add_billing_reference(test_sessionmaker, membership_id: str, suffix: str) -> None:
    setup_session = test_sessionmaker()
    setup_session.add(
        MembershipBillingReferenceOrmModel(
            id=f"billing-{suffix}",
            membership_id=membership_id,
            external_invoice_id=f"external-{suffix}",
            external_invoice_reference=f"local-{suffix}",
            due_date=date(2026, 6, 1),
            status="OPEN",
            created_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
            updated_at=datetime.fromisoformat("2026-01-01T10:00:00+00:00"),
        )
    )
    setup_session.commit()
    setup_session.close()


def test_membership_pause_active_membership_extends_end_date_without_side_effects(
    tmp_path: Path,
    monkeypatch,
) -> None:
    membership_id = "10000000-0000-0000-0000-000000000001"
    test_sessionmaker, client = _membership_lifecycle_test_client(tmp_path, monkeypatch)
    _add_membership(test_sessionmaker, membership_id, "ACTIVE", date(2027, 1, 31))
    _add_billing_reference(test_sessionmaker, membership_id, "pause")

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{membership_id}/pause",
        json={
            "pauseStartDate": "2026-06-01",
            "pauseEndDate": "2026-06-14",
            "reason": "Vacation",
        },
    )

    assert response.status_code == 200
    assert response.json()["previousStatus"] == "ACTIVE"
    assert response.json()["newStatus"] == "PAUSED"
    assert response.json()["previousEndDate"] == "2027-01-31"
    assert response.json()["newEndDate"] == "2027-02-14"
    verification_session = test_sessionmaker()
    membership = verification_session.get(MembershipOrmModel, membership_id)
    assert membership.status == "PAUSED"
    assert str(membership.pause_start_date) == "2026-06-01"
    assert str(membership.pause_end_date) == "2026-06-14"
    assert membership.pause_reason == "Vacation"
    assert verification_session.query(MembershipBillingReferenceOrmModel).count() == 1
    verification_session.close()
    assert external_invoice_store.list_invoices() == []
    assert email_service.sent_emails() == []
    app.dependency_overrides.clear()


def test_membership_pause_rejects_suspended_cancelled_and_invalid_date_range(
    tmp_path: Path,
    monkeypatch,
) -> None:
    suspended_id = "10000000-0000-0000-0000-000000000002"
    cancelled_id = "10000000-0000-0000-0000-000000000003"
    active_id = "10000000-0000-0000-0000-000000000004"
    test_sessionmaker, client = _membership_lifecycle_test_client(tmp_path, monkeypatch)
    _add_membership(test_sessionmaker, suspended_id, "SUSPENDED", date(2027, 1, 31), "NON_PAYMENT")
    _add_membership(test_sessionmaker, cancelled_id, "CANCELLED", date(2027, 1, 31))
    _add_membership(test_sessionmaker, active_id, "ACTIVE", date(2027, 1, 31))

    suspended_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{suspended_id}/pause",
        json={"pauseStartDate": "2026-06-01", "pauseEndDate": "2026-06-14"},
    )
    cancelled_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{cancelled_id}/pause",
        json={"pauseStartDate": "2026-06-01", "pauseEndDate": "2026-06-14"},
    )
    invalid_range_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{active_id}/pause",
        json={"pauseStartDate": "2026-06-14", "pauseEndDate": "2026-06-01"},
    )

    assert suspended_response.status_code == 400
    assert suspended_response.json()["message"] == "Only active memberships can be paused"
    assert cancelled_response.status_code == 400
    assert cancelled_response.json()["message"] == "Only active memberships can be paused"
    assert invalid_range_response.status_code == 400
    assert (
        invalid_range_response.json()["message"]
        == "pauseEndDate must not be before pauseStartDate"
    )
    app.dependency_overrides.clear()


def test_membership_resume_paused_membership_preserves_end_date_and_billing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    membership_id = "10000000-0000-0000-0000-000000000005"
    test_sessionmaker, client = _membership_lifecycle_test_client(tmp_path, monkeypatch)
    _add_membership(test_sessionmaker, membership_id, "PAUSED", date(2027, 2, 14))
    setup_session = test_sessionmaker()
    membership = setup_session.get(MembershipOrmModel, membership_id)
    membership.pause_start_date = date(2026, 6, 1)
    membership.pause_end_date = date(2026, 6, 14)
    membership.pause_reason = "Vacation"
    setup_session.commit()
    setup_session.close()
    _add_billing_reference(test_sessionmaker, membership_id, "resume")

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{membership_id}/resume",
        json={"resumedAt": "2026-06-10T10:00:00Z", "reason": "Back early"},
    )

    assert response.status_code == 200
    assert response.json()["previousStatus"] == "PAUSED"
    assert response.json()["newStatus"] == "ACTIVE"
    assert response.json()["previousPauseStartDate"] == "2026-06-01"
    assert response.json()["previousPauseEndDate"] == "2026-06-14"
    assert response.json()["endDate"] == "2027-02-14"
    verification_session = test_sessionmaker()
    membership = verification_session.get(MembershipOrmModel, membership_id)
    assert membership.status == "ACTIVE"
    assert membership.pause_start_date is None
    assert verification_session.query(MembershipBillingReferenceOrmModel).count() == 1
    verification_session.close()
    assert external_invoice_store.list_invoices() == []
    assert email_service.sent_emails() == []
    app.dependency_overrides.clear()


def test_membership_resume_rejects_active_membership(tmp_path: Path, monkeypatch) -> None:
    membership_id = "10000000-0000-0000-0000-000000000006"
    test_sessionmaker, client = _membership_lifecycle_test_client(tmp_path, monkeypatch)
    _add_membership(test_sessionmaker, membership_id, "ACTIVE", date(2027, 1, 31))

    response = client.post(f"{MEMBERSHIPS_BASE_PATH}/{membership_id}/resume", json={})

    assert response.status_code == 400
    assert response.json()["message"] == "Only paused memberships can be resumed"
    app.dependency_overrides.clear()


def test_membership_pause_resume_and_extend_reject_expired_memberships(
    tmp_path: Path,
    monkeypatch,
) -> None:
    active_id = "10000000-0000-0000-0000-000000000013"
    paused_id = "10000000-0000-0000-0000-000000000014"
    test_sessionmaker, client = _membership_lifecycle_test_client(tmp_path, monkeypatch)
    _add_membership(test_sessionmaker, active_id, "ACTIVE", date(2025, 12, 31))
    _add_membership(test_sessionmaker, paused_id, "PAUSED", date(2025, 12, 31))

    pause_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{active_id}/pause",
        json={"pauseStartDate": "2026-06-01", "pauseEndDate": "2026-06-14"},
    )
    resume_response = client.post(f"{MEMBERSHIPS_BASE_PATH}/{paused_id}/resume", json={})
    extend_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{active_id}/extend",
        json={"additionalDays": 10},
    )

    assert pause_response.status_code == 400
    assert pause_response.json()["message"] == "Expired memberships cannot be paused"
    assert resume_response.status_code == 400
    assert resume_response.json()["message"] == "Expired memberships cannot be resumed"
    assert extend_response.status_code == 400
    assert extend_response.json()["message"] == "Expired memberships cannot be extended"
    app.dependency_overrides.clear()


def test_membership_cancel_paused_membership_and_reject_second_cancellation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    membership_id = "10000000-0000-0000-0000-000000000007"
    test_sessionmaker, client = _membership_lifecycle_test_client(tmp_path, monkeypatch)
    _add_membership(test_sessionmaker, membership_id, "PAUSED", date(2027, 1, 31))

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{membership_id}/cancel",
        json={"cancelledAt": "2026-06-15T10:00:00Z", "reason": "Moving away"},
    )
    second_response = client.post(f"{MEMBERSHIPS_BASE_PATH}/{membership_id}/cancel", json={})

    assert response.status_code == 200
    assert response.json()["previousStatus"] == "PAUSED"
    assert response.json()["newStatus"] == "CANCELLED"
    assert response.json()["reason"] == "Moving away"
    assert second_response.status_code == 400
    assert second_response.json()["message"] == "Membership is already cancelled"
    verification_session = test_sessionmaker()
    assert verification_session.get(MembershipOrmModel, membership_id).status == "CANCELLED"
    verification_session.close()
    assert external_invoice_store.list_invoices() == []
    assert email_service.sent_emails() == []
    app.dependency_overrides.clear()


def test_membership_payment_for_cancelled_membership_marks_billing_paid_without_reactivation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    membership_id = "10000000-0000-0000-0000-000000000008"
    test_sessionmaker, client = _membership_lifecycle_test_client(tmp_path, monkeypatch)
    _add_membership(test_sessionmaker, membership_id, "CANCELLED", date(2027, 1, 31))
    _add_billing_reference(test_sessionmaker, membership_id, "cancelled-payment")

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/payment-received",
        json={
            "externalInvoiceId": "external-cancelled-payment",
            "paidAt": "2026-06-15T10:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json()["previousMembershipStatus"] == "CANCELLED"
    assert response.json()["newMembershipStatus"] == "CANCELLED"
    assert response.json()["reactivated"] is False
    assert (
        response.json()["message"]
        == "Payment recorded; membership is cancelled and remains unchanged"
    )
    verification_session = test_sessionmaker()
    assert verification_session.get(MembershipOrmModel, membership_id).status == "CANCELLED"
    billing_reference = verification_session.get(
        MembershipBillingReferenceOrmModel, "billing-cancelled-payment"
    )
    assert billing_reference.status == "PAID"
    verification_session.close()
    app.dependency_overrides.clear()


def test_membership_non_billable_extension_preserves_status_and_does_not_create_billing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    membership_id = "10000000-0000-0000-0000-000000000009"
    test_sessionmaker, client = _membership_lifecycle_test_client(tmp_path, monkeypatch)
    _add_membership(test_sessionmaker, membership_id, "PAUSED", date(2027, 1, 31))
    _add_billing_reference(test_sessionmaker, membership_id, "extension-existing")

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{membership_id}/extend",
        json={"additionalMonths": 1, "additionalDays": 5, "billable": False},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "PAUSED"
    assert response.json()["previousEndDate"] == "2027-01-31"
    assert response.json()["newEndDate"] == "2027-03-05"
    assert response.json()["billable"] is False
    assert response.json()["billingReferenceId"] is None
    verification_session = test_sessionmaker()
    assert verification_session.query(MembershipBillingReferenceOrmModel).count() == 1
    verification_session.close()
    assert external_invoice_store.list_invoices() == []
    assert email_service.sent_emails() == []
    app.dependency_overrides.clear()


def test_membership_billable_extension_creates_external_invoice_and_billing_reference(
    tmp_path: Path,
    monkeypatch,
) -> None:
    membership_id = "10000000-0000-0000-0000-000000000010"
    test_sessionmaker, client = _membership_lifecycle_test_client(tmp_path, monkeypatch)
    _add_membership(test_sessionmaker, membership_id, "SUSPENDED", date(2027, 1, 31), "NON_PAYMENT")

    response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{membership_id}/extend",
        json={"additionalDays": 10, "billable": True, "price": 250},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "SUSPENDED"
    assert response.json()["newEndDate"] == "2027-02-10"
    assert response.json()["billable"] is True
    assert response.json()["billingReferenceId"] is not None
    assert len(external_invoice_store.list_invoices()) == 1
    assert external_invoice_store.list_invoices()[0].amount_in_cents == 250
    verification_session = test_sessionmaker()
    assert verification_session.query(MembershipBillingReferenceOrmModel).count() == 1
    verification_session.close()
    assert email_service.sent_emails() == []
    app.dependency_overrides.clear()


def test_membership_extension_rejects_cancelled_invalid_duration_and_missing_price(
    tmp_path: Path,
    monkeypatch,
) -> None:
    cancelled_id = "10000000-0000-0000-0000-000000000011"
    active_id = "10000000-0000-0000-0000-000000000012"
    test_sessionmaker, client = _membership_lifecycle_test_client(tmp_path, monkeypatch)
    _add_membership(test_sessionmaker, cancelled_id, "CANCELLED", date(2027, 1, 31))
    _add_membership(test_sessionmaker, active_id, "ACTIVE", date(2027, 1, 31))

    cancelled_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{cancelled_id}/extend",
        json={"additionalDays": 10},
    )
    invalid_duration_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{active_id}/extend",
        json={"additionalDays": 0},
    )
    missing_price_response = client.post(
        f"{MEMBERSHIPS_BASE_PATH}/{active_id}/extend",
        json={"additionalDays": 10, "billable": True},
    )

    assert cancelled_response.status_code == 400
    assert cancelled_response.json()["message"] == "Cancelled memberships cannot be extended"
    assert invalid_duration_response.status_code == 400
    assert invalid_duration_response.json()["message"] == "Extension duration must be positive"
    assert missing_price_response.status_code == 400
    assert (
        missing_price_response.json()["message"]
        == "Billable extensions require a positive price"
    )
    app.dependency_overrides.clear()
