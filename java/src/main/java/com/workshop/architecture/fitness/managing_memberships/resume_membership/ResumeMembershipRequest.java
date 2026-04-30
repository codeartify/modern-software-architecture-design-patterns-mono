package com.workshop.architecture.fitness.managing_memberships.resume_membership;

import java.time.Instant;

public record ResumeMembershipRequest(
        Instant resumedAt,
        String reason
) {
}
