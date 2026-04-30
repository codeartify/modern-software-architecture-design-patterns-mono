package com.workshop.architecture.fitness.cancel_membership;

import java.time.Instant;

public record CancelMembershipRequest(
        Instant cancelledAt,
        String reason
) {
}
