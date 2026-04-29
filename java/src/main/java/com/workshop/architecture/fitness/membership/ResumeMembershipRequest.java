package com.workshop.architecture.fitness.membership;

import java.time.Instant;

public record ResumeMembershipRequest(
        Instant resumedAt,
        String reason
) {
}
