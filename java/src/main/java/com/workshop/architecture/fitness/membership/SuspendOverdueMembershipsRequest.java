package com.workshop.architecture.fitness.membership;

import java.time.Instant;

public record SuspendOverdueMembershipsRequest(
        Instant checkedAt
) {
}
