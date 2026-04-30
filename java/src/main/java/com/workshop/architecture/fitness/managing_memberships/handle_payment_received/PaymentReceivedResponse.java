package com.workshop.architecture.fitness.managing_memberships.handle_payment_received;

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
