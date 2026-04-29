package com.workshop.architecture.fitness.presentation;

import com.workshop.architecture.fitness.infrastructure.PlanEntity;

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
