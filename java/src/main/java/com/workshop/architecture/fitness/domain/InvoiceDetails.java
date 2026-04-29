package com.workshop.architecture.fitness.domain;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

public record InvoiceDetails(UUID id, UUID customerId, UUID membershipId,
                             UUID planId, LocalDate dueDate, String planTitle, BigDecimal planPrice) {
}
