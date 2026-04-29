package com.workshop.architecture.fitness.business;

public record ActivateMembershipInput(String customerId, String planId, Boolean signedByCustodian) {
}
