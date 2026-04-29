package com.workshop.architecture.fitness.clean_architecture.entity;

import java.time.LocalDate;
import java.time.Period;

public record Customer(java.util.UUID id, LocalDate dateOfBirth, String emailAddress) {

    public static final int LEGAL_AGE = 18;

    public boolean isUnderageAt(LocalDate date) {
        return Period.between(dateOfBirth(), date).getYears() < LEGAL_AGE;
    }
}
