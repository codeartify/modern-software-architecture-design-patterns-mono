package com.workshop.architecture.fitness.business.application;

public record ActivateMembershipInput(String customerId, String planId, Boolean signedByCustodian) {
}
