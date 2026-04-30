package com.workshop.architecture.fitness.infrastructure;

import com.workshop.architecture.fitness.presentation.CustomerUpsertRequest;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDate;
import java.util.Map;
import java.util.UUID;

@Entity
@Table(name = "customers")
public class CustomerEntity {

    @Id
    private UUID id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private LocalDate dateOfBirth;

    @Column(nullable = false, unique = true)
    private String emailAddress;

    protected CustomerEntity() {
    }

    public CustomerEntity(UUID id, String name, LocalDate dateOfBirth, String emailAddress) {
        this.id = id;
        this.name = name;
        this.dateOfBirth = dateOfBirth;
        this.emailAddress = emailAddress;
    }

    public UUID getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public LocalDate getDateOfBirth() {
        return dateOfBirth;
    }

    public String getEmailAddress() {
        return emailAddress;
    }

    public void updateFrom(CustomerUpsertRequest request) {
        this.name = request.name();
        this.dateOfBirth = request.dateOfBirth();
        this.emailAddress = request.emailAddress();
    }

    public static record ExternalInvoiceProviderUpsertRequest(
            @NotBlank String customerReference,
            @NotBlank String contractReference,
            @Min(0) int amountInCents,
            @NotBlank String currency,
            @NotNull LocalDate dueDate,
            @NotNull ExternalInvoiceProviderStatus status,
            String description,
            String externalCorrelationId,
            Map<String, String> metadata
    ) {
    }
}
