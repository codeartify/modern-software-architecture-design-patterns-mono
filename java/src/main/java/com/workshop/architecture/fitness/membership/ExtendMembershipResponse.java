package com.workshop.architecture.fitness.membership;

import java.time.LocalDate;

public record ExtendMembershipResponse(
        String membershipId,
        String status,
        LocalDate previousEndDate,
        LocalDate newEndDate,
        boolean billable,
        String billingReferenceId,
        String externalInvoiceReference,
        String externalInvoiceId,
        LocalDate invoiceDueDate,
        String message
) {
}
