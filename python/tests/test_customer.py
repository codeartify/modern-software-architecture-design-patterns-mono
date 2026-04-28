from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from workshop_api.fitness.customer import database
from workshop_api.fitness.customer.database import Base
from workshop_api.fitness.customer.models import CustomerOrmModel
from workshop_api.main import app


def test_customer_crud_flow(tmp_path: Path) -> None:
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'customer-test.db'}",
        connect_args={"check_same_thread": False},
    )
    test_sessionmaker = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=test_engine, tables=[CustomerOrmModel.__table__])

    def get_test_db():
        session = test_sessionmaker()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[database.get_db_session] = get_test_db
    client = TestClient(app)

    create_response = client.post(
        "/api/customers",
        json={
            "name": "Ada Example",
            "dateOfBirth": "1986-08-13",
            "emailAddress": "ada@example.com",
        },
    )

    assert create_response.status_code == 201
    customer_id = create_response.json()["id"]

    get_response = client.get(f"/api/customers/{customer_id}")
    assert get_response.status_code == 200
    assert get_response.json()["dateOfBirth"] == "1986-08-13"

    update_response = client.put(
        f"/api/customers/{customer_id}",
        json={
            "name": "Ada Lovelace",
            "dateOfBirth": "1986-08-13",
            "emailAddress": "ada.lovelace@example.com",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Ada Lovelace"

    list_response = client.get("/api/customers")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    delete_response = client.delete(f"/api/customers/{customer_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/customers/{customer_id}")
    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "status": 404,
        "error": "Not Found",
        "message": f"Customer {customer_id} was not found",
        "path": f"/api/customers/{customer_id}",
    }

    app.dependency_overrides.clear()


def test_customer_get_rejects_malformed_customer_id() -> None:
    client = TestClient(app)

    response = client.get("/api/customers/not-a-uuid")

    assert response.status_code == 400
    assert response.json() == {
        "status": 400,
        "error": "Bad Request",
        "message": "Invalid value for 'customerId': not-a-uuid",
        "path": "/api/customers/not-a-uuid",
    }
