package com.workshop.architecture.fitness.clean_architecture.entity;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

public record InvoiceDetails(UUID id, UUID customerId, UUID membershipId,
                             UUID planId, LocalDate dueDate, String planTitle, BigDecimal planPrice) {
}
