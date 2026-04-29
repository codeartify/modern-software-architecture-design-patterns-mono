package com.workshop.architecture.fitness.clean_architecture.entity;

import java.math.BigDecimal;
import java.util.UUID;

public record Plan(UUID id, BigDecimal price, int durationInMonths, String title) {
}
