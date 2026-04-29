package com.workshop.architecture.fitness.membership;

import java.time.Instant;

public record CancelMembershipRequest(
        Instant cancelledAt,
        String reason
) {
}
