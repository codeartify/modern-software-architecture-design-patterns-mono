package com.workshop.architecture.fitness.plan;

import java.math.BigDecimal;
import java.util.UUID;

public record SharedPlanResponse(
        UUID id,
        String title,
        String description,
        int durationInMonths,
        BigDecimal price
) {
    public static SharedPlanResponse fromEntity(SharedPlanEntity entity) {
        return new SharedPlanResponse(
                entity.getId(),
                entity.getTitle(),
                entity.getDescription(),
                entity.getDurationInMonths(),
                entity.getPrice()
        );
    }
}
