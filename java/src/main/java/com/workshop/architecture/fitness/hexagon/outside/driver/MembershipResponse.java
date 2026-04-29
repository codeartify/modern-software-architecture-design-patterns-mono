package com.workshop.architecture.fitness.hexagon.outside.driver;

import java.time.LocalDate;

public record MembershipResponse(
        String membershipId,
        String customerId,
        String planId,
        int planPrice,
        int planDuration,
        String status,
        String reason,
        LocalDate startDate,
        LocalDate endDate
) {

}
