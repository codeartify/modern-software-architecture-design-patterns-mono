package com.workshop.architecture.fitness.domain;

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
}
