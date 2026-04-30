package com.workshop.architecture.fitness;

import java.time.Instant;

public record CancelMembershipRequest(
        Instant cancelledAt,
        String reason
) {
}
