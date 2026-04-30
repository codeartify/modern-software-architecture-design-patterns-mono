package com.workshop.architecture.fitness;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDate;
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
}
