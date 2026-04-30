package com.workshop.architecture.fitness.managing_memberships.extend_membership;

public record ExtendMembershipRequest(
        Integer additionalMonths,
        Integer additionalDays,
        Boolean billable,
        Integer price,
        String reason
) {
}
