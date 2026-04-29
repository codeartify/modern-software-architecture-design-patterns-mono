package com.workshop.architecture.fitness.domain;

import java.time.LocalDate;

public record Customer(LocalDate dateOfBirth, String emailAddress) {
}
