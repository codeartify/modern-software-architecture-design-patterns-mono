package com.workshop.architecture.fitness.managing_memberships.shared;

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

    public Instant getCancelledAt() {
        return cancelledAt;
    }

    public String getCancellationReason() {
        return cancellationReason;
    }

    public boolean isActive() {
        return "ACTIVE".equals(status);
    }

    public boolean isPaused() {
        return "PAUSED".equals(status);
    }

    public boolean isSuspended() {
        return "SUSPENDED".equals(status);
    }

    public boolean isSuspendedForNonPayment() {
        return isSuspended() && "NON_PAYMENT".equals(reason);
    }

    // Is this domain or data access?
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

    public void pause(LocalDate pauseStartDate, LocalDate pauseEndDate, String reason) {
        long pauseDays = ChronoUnit.DAYS.between(pauseStartDate, pauseEndDate) + 1;
        this.status = "PAUSED";
        this.pauseStartDate = pauseStartDate;
        this.pauseEndDate = pauseEndDate;
        this.pauseReason = reason;
        this.endDate = this.endDate.plusDays(pauseDays);
    }

    public void resumeAfterPause() {
        this.status = "ACTIVE";
        this.pauseStartDate = null;
        this.pauseEndDate = null;
        this.pauseReason = null;
    }

    public void cancel(Instant cancelledAt, String reason) {
        this.status = "CANCELLED";
        this.cancelledAt = cancelledAt;
        this.cancellationReason = reason;
    }

    public void extendBy(int additionalMonths, int additionalDays) {
        this.endDate = this.endDate.plusMonths(additionalMonths).plusDays(additionalDays);
    }
}
