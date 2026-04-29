package com.workshop.architecture.fitness.clean_architecture.entity;

import org.jspecify.annotations.NonNull;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

public record MembershipInvoiceDetails(UUID id, UUID customerId, UUID membershipId,
                                       UUID planId, LocalDate dueDate, String planTitle, BigDecimal planPrice) {

    public static final int INVOICE_DUE_DAYS = 30;

    public static @NonNull MembershipInvoiceDetails create(UUID customerId, Membership membership, Plan plan) {
        var invoiceDueDate = LocalDate.now().plusDays(INVOICE_DUE_DAYS);

        return new MembershipInvoiceDetails(
                UUID.randomUUID(),
                customerId,
                membership.id(),
                plan.id(),
                invoiceDueDate,
                plan.title(),
                plan.price());
    }
}
