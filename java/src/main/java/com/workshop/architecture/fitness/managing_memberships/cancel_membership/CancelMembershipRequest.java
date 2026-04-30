package com.workshop.architecture.fitness.managing_memberships.cancel_membership;

import java.time.Instant;

public record CancelMembershipRequest(
        Instant cancelledAt,
        String reason
) {
}
