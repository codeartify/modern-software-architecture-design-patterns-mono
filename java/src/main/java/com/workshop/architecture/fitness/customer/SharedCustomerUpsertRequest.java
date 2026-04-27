package com.workshop.architecture.fitness.customer;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;

public record SharedCustomerUpsertRequest(
        @NotBlank String name,
        @NotNull LocalDate dateOfBirth,
        @NotBlank @Email String emailAddress
) {
}
