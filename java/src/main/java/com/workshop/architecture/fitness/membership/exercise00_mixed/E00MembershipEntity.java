package com.workshop.architecture.fitness.membership.exercise00_mixed;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

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

    protected E00MembershipEntity() {
    }

    public E00MembershipEntity(UUID id, String customerId, String planId, int planPrice, int planDuration) {
        this.id = id;
        this.customerId = customerId;
        this.planId = planId;
        this.planPrice = planPrice;
        this.planDuration = planDuration;
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
}
