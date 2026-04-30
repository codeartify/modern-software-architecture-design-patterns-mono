package com.workshop.architecture.fitness;

import java.time.Instant;

public record CancelMembershipResponse(
        String membershipId,
        String previousStatus,
        String newStatus,
        Instant cancelledAt,
        String reason,
        String message
) {
}
