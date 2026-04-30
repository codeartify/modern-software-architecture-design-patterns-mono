from enum import StrEnum


class InvoiceProviderStatus(StrEnum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
