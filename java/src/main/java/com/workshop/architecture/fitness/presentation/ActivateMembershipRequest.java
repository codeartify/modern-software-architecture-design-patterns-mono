package com.workshop.architecture.fitness.presentation;

import jakarta.validation.constraints.NotBlank;

public record ActivateMembershipRequest(
        @NotBlank String customerId,
        @NotBlank String planId,
        Boolean signedByCustodian
) {
}
