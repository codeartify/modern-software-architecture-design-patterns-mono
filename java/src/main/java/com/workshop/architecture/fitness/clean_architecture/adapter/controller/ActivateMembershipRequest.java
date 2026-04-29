package com.workshop.architecture.fitness.clean_architecture.adapter.controller;

import jakarta.validation.constraints.NotBlank;

public record ActivateMembershipRequest(
        @NotBlank String customerId,
        @NotBlank String planId,
        Boolean signedByCustodian
) {
}
