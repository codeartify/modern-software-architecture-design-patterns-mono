package com.workshop.architecture.fitness.managing_memberships.suspend_membership;

import java.time.Instant;

public record SuspendOverdueMembershipsRequest(
        Instant checkedAt
) {
}
