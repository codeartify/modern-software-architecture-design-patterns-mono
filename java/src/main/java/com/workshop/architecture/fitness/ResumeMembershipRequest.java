package com.workshop.architecture.fitness;

import java.time.Instant;

public record ResumeMembershipRequest(
        Instant resumedAt,
        String reason
) {
}
