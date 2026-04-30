package com.workshop.architecture.fitness;

import java.time.Instant;

public record SuspendOverdueMembershipsRequest(
        Instant checkedAt
) {
}
