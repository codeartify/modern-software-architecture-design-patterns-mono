package com.workshop.architecture.fitness.membership;

import java.time.Instant;
import java.util.List;

public record SuspendOverdueMembershipsResponse(
        Instant checkedAt,
        int checkedMemberships,
        List<String> suspendedMembershipIds
) {
}
