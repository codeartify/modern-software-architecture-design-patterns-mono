package com.workshop.architecture.fitness.managing_memberships.activate_membership;

import jakarta.validation.constraints.NotBlank;

public record ActivateMembershipRequest(
        @NotBlank String customerId,
        @NotBlank String planId,
        Boolean signedByCustodian
) {
}
