from fastapi.testclient import TestClient

from workshop_api.fitness.external_invoice_provider.router import store
from workshop_api.main import app


def test_external_invoice_provider_crud_flow() -> None:
    store.clear()
    client = TestClient(app)

    create_response = client.post(
        "/api/external-invoice-provider/invoices",
        json={
            "customerReference": "customer-adult-1",
            "contractReference": "membership-001",
            "amountInCents": 99900,
            "currency": "CHF",
            "dueDate": "2026-05-27",
            "status": "OPEN",
            "description": "Annual membership invoice",
            "externalCorrelationId": "activation-123",
            "metadata": {
                "origin": "fitness-system",
            },
        },
    )

    assert create_response.status_code == 201
    invoice_id = create_response.json()["invoiceId"]

    get_response = client.get(f"/api/external-invoice-provider/invoices/{invoice_id}")
    assert get_response.status_code == 200
    assert get_response.json()["contractReference"] == "membership-001"

    update_response = client.put(
        f"/api/external-invoice-provider/invoices/{invoice_id}",
        json={
            "customerReference": "customer-adult-1",
            "contractReference": "membership-001",
            "amountInCents": 99900,
            "currency": "CHF",
            "dueDate": "2026-05-27",
            "status": "PAID",
            "description": "Annual membership invoice paid",
            "externalCorrelationId": "payment-456",
            "metadata": {
                "origin": "fitness-system",
                "paymentReference": "pay-123",
            },
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "PAID"

    list_response = client.get("/api/external-invoice-provider/invoices")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    delete_response = client.delete(f"/api/external-invoice-provider/invoices/{invoice_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/external-invoice-provider/invoices/{invoice_id}")
    assert missing_response.status_code == 404
