package com.workshop.architecture.fitness.clean_architecture.entity;

import org.jspecify.annotations.NonNull;

import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

public record MembershipBillingReference(UUID id,
                                         UUID membershipId,
                                         String externalInvoiceId,
                                         String externalInvoiceReference,
                                         LocalDate dueDate,
                                         String status,
                                         Instant createdAt,
                                         Instant updatedAt) {

    public static @NonNull MembershipBillingReference create(Membership membership, String externalInvoiceId, MembershipInvoiceDetails membershipInvoiceDetails) {
        var now = Instant.now();
        return new MembershipBillingReference(
                UUID.randomUUID(),
                membership.id(),
                externalInvoiceId,
                membershipInvoiceDetails.membershipId().toString(),
                membershipInvoiceDetails.dueDate(),
                "OPEN",
                now,
                now
        );
    }
}
