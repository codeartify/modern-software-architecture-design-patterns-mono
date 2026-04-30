package com.workshop.architecture.fitness.membership.cancel_membership;

import java.time.Instant;

public record CancelMembershipRequest(
        Instant cancelledAt,
        String reason
) {
}
