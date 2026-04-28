package com.workshop.architecture.fitness.membership.exercise00_mixed;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDate;
import java.util.UUID;

@Entity
@Table(name = "memberships")
public class E00MembershipEntity {

    @Id
    private UUID id;

    @Column(nullable = false)
    private String customerId;

    @Column(nullable = false)
    private String planId;

    @Column(nullable = false)
    private int planPrice;

    @Column(nullable = false)
    private int planDuration;

    @Column(nullable = false)
    private String status;

    @Column
    private String reason;

    @Column(nullable = false)
    private LocalDate startDate;

    @Column(nullable = false)
    private LocalDate endDate;

    protected E00MembershipEntity() {
    }

    public E00MembershipEntity(
            UUID id,
            String customerId,
            String planId,
            int planPrice,
            int planDuration,
            String status,
            String reason,
            LocalDate startDate,
            LocalDate endDate
    ) {
        this.id = id;
        this.customerId = customerId;
        this.planId = planId;
        this.planPrice = planPrice;
        this.planDuration = planDuration;
        this.status = status;
        this.reason = reason;
        this.startDate = startDate;
        this.endDate = endDate;
    }

    public UUID getId() {
        return id;
    }

    public String getCustomerId() {
        return customerId;
    }

    public String getPlanId() {
        return planId;
    }

    public int getPlanPrice() {
        return planPrice;
    }

    public int getPlanDuration() {
        return planDuration;
    }

    public String getStatus() {
        return status;
    }

    public String getReason() {
        return reason;
    }

    public LocalDate getStartDate() {
        return startDate;
    }

    public LocalDate getEndDate() {
        return endDate;
    }

    public boolean isActive() {
        return "ACTIVE".equals(status);
    }

    public boolean isSuspended() {
        return "SUSPENDED".equals(status);
    }

    public boolean isSuspendedForNonPayment() {
        return isSuspended() && "NON_PAYMENT".equals(reason);
    }

    public boolean isCancelled() {
        return "CANCELLED".equals(status);
    }

    public void suspend() {
        this.status = "SUSPENDED";
    }

    public void suspendForNonPayment() {
        this.status = "SUSPENDED";
        this.reason = "NON_PAYMENT";
    }

    public void reactivateAfterPayment() {
        this.status = "ACTIVE";
        this.reason = null;
    }
}
