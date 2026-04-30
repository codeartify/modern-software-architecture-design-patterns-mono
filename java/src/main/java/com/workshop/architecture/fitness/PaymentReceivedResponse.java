package com.workshop.architecture.fitness;

import java.time.Instant;

public record PaymentReceivedResponse(
        Instant paidAt,
        String membershipId,
        String billingReferenceId,
        String previousMembershipStatus,
        String newMembershipStatus,
        boolean reactivated,
        String message
) {
}
