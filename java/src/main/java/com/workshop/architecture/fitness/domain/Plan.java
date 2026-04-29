package com.workshop.architecture.fitness.domain;

import java.math.BigDecimal;
import java.util.UUID;

public record Plan(UUID id, BigDecimal price, int durationInMonths, String title) {
}
