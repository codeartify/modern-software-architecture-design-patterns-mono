package com.workshop.architecture.fitness;

public record ExtendMembershipRequest(
        Integer additionalMonths,
        Integer additionalDays,
        Boolean billable,
        Integer price,
        String reason
) {
}
