package com.workshop.architecture.fitness.managing_memberships.shared;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "membership_billing_references")
public class MembershipBillingReferenceEntity {

    @Id
    private UUID id;

    @Column(nullable = false)
    private UUID membershipId;

    @Column(nullable = false, unique = true)
    private String externalInvoiceId;

    @Column(nullable = false, unique = true)
    private String externalInvoiceReference;

    @Column(nullable = false)
    private LocalDate dueDate;

    @Column(nullable = false)
    private String status;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    protected MembershipBillingReferenceEntity() {
    }

    public MembershipBillingReferenceEntity(
            UUID id,
            UUID membershipId,
            String externalInvoiceId,
            String externalInvoiceReference,
            LocalDate dueDate,
            String status,
            Instant createdAt,
            Instant updatedAt
    ) {
        this.id = id;
        this.membershipId = membershipId;
        this.externalInvoiceId = externalInvoiceId;
        this.externalInvoiceReference = externalInvoiceReference;
        this.dueDate = dueDate;
        this.status = status;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public UUID getId() {
        return id;
    }

    public UUID getMembershipId() {
        return membershipId;
    }

    public String getExternalInvoiceId() {
        return externalInvoiceId;
    }

    public String getExternalInvoiceReference() {
        return externalInvoiceReference;
    }

    public LocalDate getDueDate() {
        return dueDate;
    }

    public String getStatus() {
        return status;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public boolean isPaid() {
        return "PAID".equals(status);
    }

    public void markPaid(Instant paidAt) {
        this.status = "PAID";
        this.updatedAt = paidAt;
    }
}
