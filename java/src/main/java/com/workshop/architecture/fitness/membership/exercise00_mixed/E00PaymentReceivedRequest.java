package com.workshop.architecture.fitness.membership.exercise00_mixed;

import java.time.Instant;

public record E00PaymentReceivedRequest(
        String externalInvoiceId,
        String externalInvoiceReference,
        String membershipId,
        Instant paidAt
) {
}
