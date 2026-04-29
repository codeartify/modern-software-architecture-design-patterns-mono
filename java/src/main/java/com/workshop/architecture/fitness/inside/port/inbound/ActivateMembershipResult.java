package com.workshop.architecture.fitness.inside.port.inbound;

import java.time.LocalDate;

public record ActivateMembershipResult(
        String membershipId,
        String customerId,
        String planId,
        int planPrice,
        int planDuration,
        String status,
        LocalDate startDate,
        LocalDate endDate,
        String invoiceId,
        String externalInvoiceId,
        LocalDate invoiceDueDate
) {
}
