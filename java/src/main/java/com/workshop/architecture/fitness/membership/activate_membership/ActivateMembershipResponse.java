package com.workshop.architecture.fitness.membership.activate_membership;

import java.time.LocalDate;

public record ActivateMembershipResponse(
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
