package com.workshop.architecture.fitness.shared.plan;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;

public record SharedPlanUpsertRequest(
        @NotBlank String title,
        @NotBlank String description,
        @Min(1) int durationInMonths,
        @NotNull @DecimalMin("0.00") BigDecimal price
) {
}
