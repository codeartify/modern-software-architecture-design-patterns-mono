package com.workshop.architecture.fitness.managing_memberships.pause_membership;

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
