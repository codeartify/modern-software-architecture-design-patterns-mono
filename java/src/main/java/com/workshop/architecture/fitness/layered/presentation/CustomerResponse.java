package com.workshop.architecture.fitness.layered.presentation;


import com.workshop.architecture.fitness.layered.infrastructure.CustomerEntity;

import java.time.LocalDate;
import java.util.UUID;

public record CustomerResponse(
        UUID id,
        String name,
        LocalDate dateOfBirth,
        String emailAddress
) {
    public static CustomerResponse fromEntity(CustomerEntity entity) {
        return new CustomerResponse(
                entity.getId(),
                entity.getName(),
                entity.getDateOfBirth(),
                entity.getEmailAddress()
        );
    }
}
