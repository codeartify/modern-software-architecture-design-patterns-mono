package com.workshop.architecture.fitness.inside.port.outbound;

import java.math.BigDecimal;
import java.util.UUID;

public record Plan(UUID id, BigDecimal price, int durationInMonths, String title) {
}
