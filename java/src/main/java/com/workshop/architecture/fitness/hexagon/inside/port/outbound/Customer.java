package com.workshop.architecture.fitness.hexagon.inside.port.outbound;

import java.time.LocalDate;

public record Customer(LocalDate dateOfBirth, String emailAddress) {
}
