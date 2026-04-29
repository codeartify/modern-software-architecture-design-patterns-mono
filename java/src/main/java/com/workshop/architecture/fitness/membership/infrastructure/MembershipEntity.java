package com.workshop.architecture.fitness.membership.infrastructure;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.Instant;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.UUID;

@Entity
@Table(name = "memberships")
public class MembershipEntity {

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

    @Column
    private LocalDate pauseStartDate;

    @Column
    private LocalDate pauseEndDate;

    @Column
    private String pauseReason;

    @Column
    private Instant cancelledAt;

    @Column
    private String cancellationReason;

    protected MembershipEntity() {
    }

    public MembershipEntity(
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

    public LocalDate getPauseStartDate() {
        return pauseStartDate;
    }

    public LocalDate getPauseEndDate() {
        return pauseEndDate;
    }

    public String getPauseReason() {
        return pauseReason;
    }


}
