package com.workshop.architecture.fitness.membership;

public record ExtendMembershipRequest(
        Integer additionalMonths,
        Integer additionalDays,
        Boolean billable,
        Integer price,
        String reason
) {
}
