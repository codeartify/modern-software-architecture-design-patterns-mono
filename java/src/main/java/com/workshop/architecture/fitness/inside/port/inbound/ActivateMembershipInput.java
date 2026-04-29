package com.workshop.architecture.fitness.inside.port.inbound;

public record ActivateMembershipInput(String customerId, String planId, Boolean signedByCustodian) {
}
