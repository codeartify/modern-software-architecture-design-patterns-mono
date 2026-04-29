package com.workshop.architecture.fitness.hexagon.inside.port.outbound;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

public record MembershipInvoiceDetails(UUID id, UUID customerId, UUID membershipId,
                                       UUID planId, LocalDate dueDate, String planTitle, BigDecimal planPrice) {
}
