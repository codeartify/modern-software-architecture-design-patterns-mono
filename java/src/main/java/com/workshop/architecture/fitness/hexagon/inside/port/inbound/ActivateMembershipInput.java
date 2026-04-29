package com.workshop.architecture.fitness.hexagon.inside.port.inbound;

public record ActivateMembershipInput(String customerId, String planId, Boolean signedByCustodian) {
}
