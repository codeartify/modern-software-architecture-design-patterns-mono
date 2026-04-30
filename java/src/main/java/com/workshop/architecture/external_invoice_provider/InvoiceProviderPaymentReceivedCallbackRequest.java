package com.workshop.architecture.external_invoice_provider;

import java.time.Instant;

public record InvoiceProviderPaymentReceivedCallbackRequest(
        String externalInvoiceId,
        String externalInvoiceReference,
        String membershipId,
        Instant paidAt
) {
}
