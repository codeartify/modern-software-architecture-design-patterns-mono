import json
import os
import uuid
from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from workshop_api.fitness.errors import NotFoundError
from workshop_api.fitness.external_invoice_provider.models import ExternalInvoiceProviderStatus
from workshop_api.fitness.external_invoice_provider.schemas import (
    ExternalInvoiceProviderPaymentReceivedCallbackRequest,
    ExternalInvoiceProviderResponse,
    ExternalInvoiceProviderUpsertRequest,
)
from workshop_api.fitness.external_invoice_provider.store import ExternalInvoiceProviderStore

router = APIRouter(
    prefix="/api/shared/external-invoice-provider/invoices",
    tags=["external-invoice-provider"],
)

store = ExternalInvoiceProviderStore()


def get_fitness_api_base_url() -> str:
    return os.getenv("WORKSHOP_FITNESS_API_BASE_URL", "http://127.0.0.1:9090")


@router.get("", response_model=list[ExternalInvoiceProviderResponse], response_model_by_alias=True)
def list_invoices() -> list[ExternalInvoiceProviderResponse]:
    return store.list_invoices()


@router.get(
    "/{invoice_id}",
    response_model=ExternalInvoiceProviderResponse,
    response_model_by_alias=True,
)
def get_invoice(invoice_id: str) -> ExternalInvoiceProviderResponse:
    invoice = store.get_invoice(invoice_id)
    if invoice is None:
        raise _not_found(invoice_id)
    return invoice


@router.post(
    "",
    response_model=ExternalInvoiceProviderResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
    request: ExternalInvoiceProviderUpsertRequest,
    response: Response,
) -> ExternalInvoiceProviderResponse:
    invoice_id = str(uuid.uuid4())
    created = store.save(invoice_id, request)
    response.headers["Location"] = f"/api/shared/external-invoice-provider/invoices/{invoice_id}"
    return created


@router.post(
    "/{invoice_id}/mark-paid",
    response_model=ExternalInvoiceProviderResponse,
    response_model_by_alias=True,
)
async def mark_invoice_paid(
    invoice_id: str,
    request: Request,
    fitness_api_base_url: str = Depends(get_fitness_api_base_url),
) -> ExternalInvoiceProviderResponse:
    invoice = store.get_invoice(invoice_id)
    if invoice is None:
        raise _not_found(invoice_id)

    if invoice.status == ExternalInvoiceProviderStatus.PAID:
        return invoice

    paid_invoice = store.save_response(
        ExternalInvoiceProviderResponse(
            invoiceId=invoice.invoice_id,
            customerReference=invoice.customer_reference,
            contractReference=invoice.contract_reference,
            amountInCents=invoice.amount_in_cents,
            currency=invoice.currency,
            dueDate=invoice.due_date,
            status=ExternalInvoiceProviderStatus.PAID,
            description=invoice.description,
            externalCorrelationId=invoice.external_correlation_id,
            metadata=invoice.metadata,
        )
    )

    callback_request = ExternalInvoiceProviderPaymentReceivedCallbackRequest(
        externalInvoiceId=paid_invoice.invoice_id,
        externalInvoiceReference=paid_invoice.external_correlation_id,
        membershipId=paid_invoice.contract_reference,
        paidAt=datetime.now(UTC),
    )

    client_kwargs: dict[str, object] = {"base_url": fitness_api_base_url}
    if fitness_api_base_url.startswith("http://testserver"):
        client_kwargs["transport"] = httpx.ASGITransport(app=request.app)

    try:
        async with httpx.AsyncClient(**client_kwargs) as client:
            callback_response = await client.post(
                "/api/e00/memberships/payment-received",
                json=callback_request.model_dump(by_alias=True, mode="json")
                if hasattr(callback_request, "model_dump")
                else json.loads(callback_request.json(by_alias=True)),
            )
            callback_response.raise_for_status()
    except httpx.HTTPError:
        pass

    return paid_invoice


@router.put(
    "/{invoice_id}",
    response_model=ExternalInvoiceProviderResponse,
    response_model_by_alias=True,
)
def update_invoice(
    invoice_id: str,
    request: ExternalInvoiceProviderUpsertRequest,
) -> ExternalInvoiceProviderResponse:
    if store.get_invoice(invoice_id) is None:
        raise _not_found(invoice_id)
    return store.save(invoice_id, request)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(invoice_id: str) -> Response:
    if store.get_invoice(invoice_id) is None:
        raise _not_found(invoice_id)
    store.delete(invoice_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _not_found(invoice_id: str) -> HTTPException:
    error = NotFoundError(f"External invoice {invoice_id} was not found")
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
