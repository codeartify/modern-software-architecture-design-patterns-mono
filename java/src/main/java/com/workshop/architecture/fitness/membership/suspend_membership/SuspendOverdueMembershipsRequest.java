package com.workshop.architecture.fitness.membership.suspend_membership;

import java.time.Instant;

public record SuspendOverdueMembershipsRequest(
        Instant checkedAt
) {
}
