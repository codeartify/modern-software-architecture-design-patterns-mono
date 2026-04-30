package com.workshop.architecture.fitness.membership.pause_membership;

import java.time.LocalDate;

public record PauseMembershipRequest(
        LocalDate pauseStartDate,
        LocalDate pauseEndDate,
        String reason
) {
}
