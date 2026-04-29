package com.workshop.architecture.fitness.clean_architecture.entity;

import org.jspecify.annotations.NonNull;

import java.time.LocalDate;

public record CustomerActivateMembershipEmail(String invoiceId, LocalDate invoiceDueDate, String emailAddress,
                                              int planPrice, String emailTemplate) {
    public static @NonNull CustomerActivateMembershipEmail toEmail(
            MembershipBillingReference billingReference,
            String emailAddress,
            int planPrice) {
        var emailTemplate = """
                |
                |To: %s
                |From: %s
                |Subject: Your Membership Invoice %s
                |
                |Dear customer,
                |
                |Thank you for your membership.
                |
                |Please find your invoice details below:
                |Invoice ID: %s
                |Amount Due: CHF %s
                |Due Date: %s
                |
                |Attachment: invoice-%s.pdf
                |
                |Kind regards,
                |Codeartify Billing
                |
                """;

        return new CustomerActivateMembershipEmail(
                billingReference.externalInvoiceReference(),
                billingReference.dueDate(),
                emailAddress,
                planPrice,
                emailTemplate);
    }
}
