package com.workshop.architecture.fitness.clean_architecture.entity;

import com.workshop.architecture.fitness.clean_architecture.use_case.exception.CustomerTooYoungException;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

import static java.lang.Boolean.TRUE;

public record Membership(
        UUID id,
        UUID customerId,
        UUID planId,
        int planPrice,
        int planDurationInMonths,
        String status,
        String statusReason,
        LocalDate startDate,
        LocalDate endDate
) {
    public static Membership create(Customer customer,
                                    UUID planId,
                                    Boolean isSignedByCustodian,
                                    LocalDate startDate,
                                    int planDurationInMonths,
                                    BigDecimal planPrice) {

        // DDD Invariant
        if (customer.isUnderageAt(startDate) && isMissingSignature(isSignedByCustodian)) {
            throw new CustomerTooYoungException(
                    "Customers younger than 18 require signedByCustodian=true"
            );
        }

        var endDate = startDate.plusMonths(planDurationInMonths);

        return new Membership(
                UUID.randomUUID(),
                customer.id(),
                planId,
                planPrice.intValue(),
                planDurationInMonths,
                "ACTIVE",
                null,
                startDate,
                endDate
        );
    }

    private static boolean isMissingSignature(Boolean isSignedByCustodian) {
        return !TRUE.equals(isSignedByCustodian);
    }
}
