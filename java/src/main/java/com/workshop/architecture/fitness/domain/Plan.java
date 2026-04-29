package com.workshop.architecture.fitness.domain;

import java.math.BigDecimal;

public record Plan(BigDecimal price, int durationInMonths, String title) {
}
