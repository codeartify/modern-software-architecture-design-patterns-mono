package com.workshop.architecture.fitness.clean_architecture.entity;

import java.time.LocalDate;
import java.util.UUID;

public record PlanDetails(
        PlanId planId,
        Price price,
        Duration duration
) {

    public int planPrice() {
        return price.amount();
    }

    public int planDurationInMonths() {
        return duration.inMonths();
    }

    public LocalDate startDate() {
        return duration.startDate();
    }

    public LocalDate endDate() {
        return duration.endDate();
    }
}
