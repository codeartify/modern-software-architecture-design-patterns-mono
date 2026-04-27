package com.workshop.architecture.fitness.membership.exercise00_mixed;

import java.time.Instant;

public record E00SuspendOverdueMembershipsRequest(
        Instant checkedAt
) {
}
