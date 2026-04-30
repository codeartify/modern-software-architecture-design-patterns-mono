package com.workshop.architecture.fitness.get_membership;

import com.workshop.architecture.fitness.shared.MembershipEntity;

import java.time.LocalDate;

public record GetMembershipResponse(
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
    static GetMembershipResponse fromEntity(MembershipEntity entity) {
        return new GetMembershipResponse(
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
