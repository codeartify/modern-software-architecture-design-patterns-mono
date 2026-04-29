package com.workshop.architecture.fitness.layered.presentation;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.LocalDate;

public record CustomerUpsertRequest(
        @NotBlank String name,
        @NotNull LocalDate dateOfBirth,
        @NotBlank @Email String emailAddress
) {
}
