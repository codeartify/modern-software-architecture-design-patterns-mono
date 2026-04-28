package com.workshop.architecture.fitness.external_invoice_provider;

import java.time.Instant;

public record ExternalInvoiceProviderPaymentReceivedCallbackRequest(
        String externalInvoiceId,
        String externalInvoiceReference,
        String membershipId,
        Instant paidAt
) {
}
