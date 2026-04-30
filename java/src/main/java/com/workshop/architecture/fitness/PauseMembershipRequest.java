package com.workshop.architecture.fitness;

import java.time.LocalDate;

public record PauseMembershipRequest(
        LocalDate pauseStartDate,
        LocalDate pauseEndDate,
        String reason
) {
}
