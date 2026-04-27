package com.workshop.architecture.fitness.shared.customer;

import java.time.LocalDate;
import java.util.UUID;

public record SharedCustomerResponse(
        UUID id,
        String name,
        LocalDate dateOfBirth,
        String emailAddress
) {
    public static SharedCustomerResponse fromEntity(SharedCustomerEntity entity) {
        return new SharedCustomerResponse(
                entity.getId(),
                entity.getName(),
                entity.getDateOfBirth(),
                entity.getEmailAddress()
        );
    }
}
