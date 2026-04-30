package com.workshop.architecture.fitness.managing_plans;

import java.math.BigDecimal;
import java.util.UUID;

public record PlanResponse(
        UUID id,
        String title,
        String description,
        int durationInMonths,
        BigDecimal price
) {
    public static PlanResponse fromEntity(PlanEntity entity) {
        return new PlanResponse(
                entity.getId(),
                entity.getTitle(),
                entity.getDescription(),
                entity.getDurationInMonths(),
                entity.getPrice()
        );
    }
}
