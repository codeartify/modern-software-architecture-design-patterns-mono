package com.workshop.architecture.fitness.membership.exercise00_mixed;

import java.time.LocalDate;

public record E00MembershipResponse(
        String membershipId,
        String customerId,
        String planId,
        int planPrice,
        int planDuration,
        String status,
        LocalDate startDate,
        LocalDate endDate
) {
    static E00MembershipResponse fromEntity(E00MembershipEntity entity) {
        return new E00MembershipResponse(
                entity.getId().toString(),
                entity.getCustomerId(),
                entity.getPlanId(),
                entity.getPlanPrice(),
                entity.getPlanDuration(),
                entity.getStatus(),
                entity.getStartDate(),
                entity.getEndDate()
        );
    }
}
