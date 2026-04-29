package com.workshop.architecture.fitness.clean_architecture.entity;

import java.time.LocalDate;
import java.util.UUID;

public record Membership(
        UUID id,
        UUID customerId,
        UUID planId,
        int planPrice,
        int planDurationInMonths,
        String status,
        String statusReason,
        LocalDate startDate,
        LocalDate endDate
) {
}
