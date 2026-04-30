package com.workshop.architecture.fitness;

import java.time.LocalDate;

public record MembershipResponse(
        String membershipId,
        String customerId,
        String planId,
        int planPrice,
        int planDuration,
        String status,
        String reason,
        LocalDate startDate,
        LocalDate endDate
) {
    static MembershipResponse fromEntity(MembershipEntity entity) {
        return new MembershipResponse(
                entity.getId().toString(),
                entity.getCustomerId(),
                entity.getPlanId(),
                entity.getPlanPrice(),
                entity.getPlanDuration(),
                entity.getStatus(),
                entity.getReason(),
                entity.getStartDate(),
                entity.getEndDate()
        );
    }
}
