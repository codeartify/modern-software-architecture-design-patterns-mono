package com.workshop.architecture.fitness.suspend_membership;

import java.time.Instant;

public record SuspendOverdueMembershipsRequest(
        Instant checkedAt
) {
}
