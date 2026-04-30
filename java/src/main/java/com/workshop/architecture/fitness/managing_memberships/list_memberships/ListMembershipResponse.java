package com.workshop.architecture.fitness.managing_memberships.list_memberships;

import com.workshop.architecture.fitness.managing_memberships.shared.MembershipEntity;

import java.time.LocalDate;

public record ListMembershipResponse(
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
    static ListMembershipResponse fromEntity(MembershipEntity entity) {
        return new ListMembershipResponse(
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
