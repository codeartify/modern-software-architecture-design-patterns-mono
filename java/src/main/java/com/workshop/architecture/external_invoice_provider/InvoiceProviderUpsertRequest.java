package com.workshop.architecture.external_invoice_provider;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDate;
import java.util.Map;

public record InvoiceProviderUpsertRequest(
        @NotBlank String customerReference,
        @NotBlank String contractReference,
        @Min(0) int amountInCents,
        @NotBlank String currency,
        @NotNull LocalDate dueDate,
        @NotNull InvoiceProviderStatus status,
        String description,
        String externalCorrelationId,
        Map<String, String> metadata
) {
}
