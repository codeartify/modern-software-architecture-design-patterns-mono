package com.workshop.architecture.fitness.clean_architecture.entity;

import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;

class PlanDetailsTest {

    @Test
    void exposesPlanDetailsThroughValueObjectsAndCompatibilityAccessors() {
        UUID planId = UUID.randomUUID();
        LocalDate startDate = LocalDate.parse("2026-01-01");
        LocalDate endDate = LocalDate.parse("2027-01-01");

        PlanDetails details = new PlanDetails(new PlanId(planId), new Price(999), new Duration(startDate, endDate));
        ;

        assertThat(details.planId()).isEqualTo(new PlanId(planId));
        assertThat(details.price()).isEqualTo(new Price(999));
        assertThat(details.duration()).isEqualTo(new Duration(startDate, endDate));
        assertThat(details.planPrice()).isEqualTo(999);
        assertThat(details.planDurationInMonths()).isEqualTo(12);
        assertThat(details.startDate()).isEqualTo(startDate);
        assertThat(details.endDate()).isEqualTo(endDate);
    }
}
