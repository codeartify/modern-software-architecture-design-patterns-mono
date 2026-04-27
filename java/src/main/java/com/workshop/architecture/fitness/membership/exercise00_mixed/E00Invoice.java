package com.workshop.architecture.fitness.membership.exercise00_mixed;

import java.time.LocalDate;

record E00Invoice(
        String id,
        String membershipId,
        String customerId,
        int amount,
        LocalDate dueDate
) {
}
