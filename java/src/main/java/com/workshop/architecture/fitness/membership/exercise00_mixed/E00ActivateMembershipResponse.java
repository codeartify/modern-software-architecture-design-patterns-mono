package com.workshop.architecture.fitness.membership.exercise00_mixed;

import java.time.LocalDate;

public record E00ActivateMembershipResponse(
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
