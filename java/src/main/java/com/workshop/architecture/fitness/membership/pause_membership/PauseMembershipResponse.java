package com.workshop.architecture.fitness.membership.pause_membership;

import java.time.LocalDate;

public record PauseMembershipResponse(
        String membershipId,
        String previousStatus,
        String newStatus,
        LocalDate pauseStartDate,
        LocalDate pauseEndDate,
        LocalDate previousEndDate,
        LocalDate newEndDate,
        String reason,
        String message
) {
}
