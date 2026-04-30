package com.workshop.architecture.external_invoice_provider;

import java.time.LocalDate;
import java.util.Map;

public record InvoiceProviderResponse(
        String invoiceId,
        String customerReference,
        String contractReference,
        int amountInCents,
        String currency,
        LocalDate dueDate,
        InvoiceProviderStatus status,
        String description,
        String externalCorrelationId,
        Map<String, String> metadata
) {
}
