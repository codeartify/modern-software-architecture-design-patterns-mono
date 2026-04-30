package com.workshop.architecture.fitness.extend_membership;

public record ExtendMembershipRequest(
        Integer additionalMonths,
        Integer additionalDays,
        Boolean billable,
        Integer price,
        String reason
) {
}
