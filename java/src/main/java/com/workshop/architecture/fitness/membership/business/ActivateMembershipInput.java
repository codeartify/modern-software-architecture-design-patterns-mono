package com.workshop.architecture.fitness.membership.business;

public record ActivateMembershipInput(String customerId, String planId, Boolean signedByCustodian) {
}
