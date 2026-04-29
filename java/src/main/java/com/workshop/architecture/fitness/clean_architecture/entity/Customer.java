package com.workshop.architecture.fitness.clean_architecture.entity;

import java.time.LocalDate;

public record Customer(LocalDate dateOfBirth, String emailAddress) {
}
