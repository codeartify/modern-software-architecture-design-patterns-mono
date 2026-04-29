package com.workshop.architecture.fitness.membership;

import java.time.Instant;

public record PaymentReceivedRequest(
        String externalInvoiceId,
        String externalInvoiceReference,
        String membershipId,
        Instant paidAt
) {
}
