from enum import StrEnum


class ExternalInvoiceProviderStatus(StrEnum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
