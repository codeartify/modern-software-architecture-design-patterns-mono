from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from workshop_api.fitness.shared.customer import database
from workshop_api.fitness.shared.customer.database import Base
from workshop_api.fitness.shared.plan.models import SharedPlanOrmModel
from workshop_api.main import app


def test_plan_crud_flow(tmp_path: Path) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'plan-test.db'}",
        connect_args={"check_same_thread": False},
    )
    test_sessionmaker = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=test_engine, tables=[SharedPlanOrmModel.__table__])

    def get_test_db():
        session = test_sessionmaker()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[database.get_db_session] = get_test_db
    client = TestClient(app)

    create_response = client.post(
        "/api/shared/plans",
        json={
            "title": "Premium 12 Months",
            "description": "Twelve months for regular training",
            "durationInMonths": 12,
            "price": "999.00",
        },
    )

    assert create_response.status_code == 201
    plan_id = create_response.json()["id"]

    get_response = client.get(f"/api/shared/plans/{plan_id}")
    assert get_response.status_code == 200
    assert get_response.json()["durationInMonths"] == 12
    assert Decimal(get_response.json()["price"]) == Decimal("999.00")

    update_response = client.put(
        f"/api/shared/plans/{plan_id}",
        json={
            "title": "Elite 24 Months",
            "description": "Twenty-four months for long-term training",
            "durationInMonths": 24,
            "price": "1699.00",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Elite 24 Months"
    assert Decimal(update_response.json()["price"]) == Decimal("1699.00")

    list_response = client.get("/api/shared/plans")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    delete_response = client.delete(f"/api/shared/plans/{plan_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/shared/plans/{plan_id}")
    assert missing_response.status_code == 404

    app.dependency_overrides.clear()
