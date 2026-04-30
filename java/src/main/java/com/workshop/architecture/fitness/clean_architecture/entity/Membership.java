package com.workshop.architecture.fitness.clean_architecture.entity;

import com.workshop.architecture.fitness.clean_architecture.use_case.exception.CustomerTooYoungException;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

import static java.lang.Boolean.TRUE;

public final class Membership {
    private final MembershipId id;
    private final CustomerId customerId;
    private final MembershipStatus status;
    private final PlanDetails planDetails;

    public Membership(MembershipId id, CustomerId customerId, MembershipStatus status, PlanDetails planDetails) {
        this.id = id;
        this.customerId = customerId;
        this.status = status;
        this.planDetails = planDetails;
    }

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
                new MembershipId(UUID.randomUUID()),
                new CustomerId(customer.id()),
                new MembershipStatus(MembershipStatusValue.ACTIVE, null),
                new PlanDetails(
                        new PlanId(planId),
                        new Price(planPrice.intValue()),
                        new Duration(startDate, endDate)
                )
        );
    }

    private static boolean isMissingSignature(Boolean isSignedByCustodian) {
        return !TRUE.equals(isSignedByCustodian);
    }

    public UUID id() {
        return id.id();
    }

    public UUID customerId() {
        return customerId.id();
    }

    public UUID planId() {
        return planDetails.planId().id();
    }

    public int planPrice() {
        return planDetails.planPrice();
    }

    public int planDurationInMonths() {
        return planDetails.planDurationInMonths();
    }

    public String status() {
        return status.value().name();
    }

    public String statusReason() {
        return status.reason();
    }

    public LocalDate startDate() {
        return planDetails.startDate();
    }

    public LocalDate endDate() {
        return planDetails.endDate();
    }


}
