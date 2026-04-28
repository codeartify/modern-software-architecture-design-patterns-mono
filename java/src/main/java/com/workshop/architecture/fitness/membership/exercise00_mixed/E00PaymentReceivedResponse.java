package com.workshop.architecture.fitness.membership.exercise00_mixed;

import java.time.Instant;

public record E00PaymentReceivedResponse(
        Instant paidAt,
        String membershipId,
        String billingReferenceId,
        String previousMembershipStatus,
        String newMembershipStatus,
        boolean reactivated,
        String message
) {
}
