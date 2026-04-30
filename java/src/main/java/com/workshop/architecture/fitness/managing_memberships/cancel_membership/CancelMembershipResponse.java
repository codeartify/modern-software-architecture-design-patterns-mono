package com.workshop.architecture.fitness.managing_memberships.cancel_membership;

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
