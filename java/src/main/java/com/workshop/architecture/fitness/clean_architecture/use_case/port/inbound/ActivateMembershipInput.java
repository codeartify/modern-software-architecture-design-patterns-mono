package com.workshop.architecture.fitness.clean_architecture.use_case.port.inbound;

public record ActivateMembershipInput(String customerId, String planId, Boolean signedByCustodian) {
}
