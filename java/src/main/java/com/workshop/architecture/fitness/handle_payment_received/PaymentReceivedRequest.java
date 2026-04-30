package com.workshop.architecture.fitness.handle_payment_received;

import java.time.Instant;

public record PaymentReceivedRequest(
        String externalInvoiceId,
        String externalInvoiceReference,
        String membershipId,
        Instant paidAt
) {
}
