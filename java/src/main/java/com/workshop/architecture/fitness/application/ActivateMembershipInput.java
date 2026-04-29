package com.workshop.architecture.fitness.application;

public record ActivateMembershipInput(String customerId, String planId, Boolean signedByCustodian) {
}
