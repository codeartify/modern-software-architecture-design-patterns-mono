package com.workshop.architecture.fitness.membership.exercise00_mixed;

import java.time.Instant;
import java.util.List;

public record E00SuspendOverdueMembershipsResponse(
        Instant checkedAt,
        int checkedMemberships,
        List<String> suspendedMembershipIds
) {
}
