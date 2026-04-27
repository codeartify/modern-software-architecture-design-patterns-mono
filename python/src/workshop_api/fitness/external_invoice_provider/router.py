import uuid

from fastapi import APIRouter, HTTPException, Response, status

from workshop_api.fitness.errors import NotFoundError
from workshop_api.fitness.external_invoice_provider.schemas import (
    ExternalInvoiceProviderResponse,
    ExternalInvoiceProviderUpsertRequest,
)
from workshop_api.fitness.external_invoice_provider.store import ExternalInvoiceProviderStore

router = APIRouter(
    prefix="/api/external-invoice-provider/invoices",
    tags=["external-invoice-provider"],
)

store = ExternalInvoiceProviderStore()


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
    response.headers["Location"] = f"/api/external-invoice-provider/invoices/{invoice_id}"
    return created


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
