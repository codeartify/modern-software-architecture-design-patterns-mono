package com.workshop.architecture.fitness.shared;


import java.time.LocalDate;
import java.util.Map;

public record ExternalInvoiceProviderResponse(
        String invoiceId,
        String customerReference,
        String contractReference,
        int amountInCents,
        String currency,
        LocalDate dueDate,
        ExternalInvoiceProviderStatus status,
        String description,
        String externalCorrelationId,
        Map<String, String> metadata
) {
}
