package com.workshop.architecture.fitness.hexagon.outside.driver;

import jakarta.validation.constraints.NotBlank;

public record ActivateMembershipRequest(
        @NotBlank String customerId,
        @NotBlank String planId,
        Boolean signedByCustodian
) {
}
