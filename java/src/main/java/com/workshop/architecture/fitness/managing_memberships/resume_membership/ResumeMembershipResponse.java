package com.workshop.architecture.fitness.managing_memberships.resume_membership;

import java.time.Instant;
import java.time.LocalDate;

public record ResumeMembershipResponse(
        String membershipId,
        String previousStatus,
        String newStatus,
        Instant resumedAt,
        LocalDate previousPauseStartDate,
        LocalDate previousPauseEndDate,
        LocalDate endDate,
        String reason,
        String message
) {
}
