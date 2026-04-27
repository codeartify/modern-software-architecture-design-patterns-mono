package com.workshop.architecture.fitness.membership.exercise00_mixed;

import jakarta.validation.constraints.NotBlank;

public record E00ActivateMembershipRequest(
        @NotBlank String customerId,
        @NotBlank String planId
) {
}
