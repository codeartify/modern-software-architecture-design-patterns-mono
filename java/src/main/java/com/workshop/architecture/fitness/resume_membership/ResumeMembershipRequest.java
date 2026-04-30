package com.workshop.architecture.fitness.resume_membership;

import java.time.Instant;

public record ResumeMembershipRequest(
        Instant resumedAt,
        String reason
) {
}
