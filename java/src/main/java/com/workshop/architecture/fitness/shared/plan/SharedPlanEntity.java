package com.workshop.architecture.fitness.shared.plan;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "plans")
public class SharedPlanEntity {

    @Id
    private UUID id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false, length = 2000)
    private String description;

    @Column(nullable = false)
    private int durationInMonths;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    protected SharedPlanEntity() {
    }

    public SharedPlanEntity(
            UUID id,
            String title,
            String description,
            int durationInMonths,
            BigDecimal price
    ) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.durationInMonths = durationInMonths;
        this.price = price;
    }

    public UUID getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getDescription() {
        return description;
    }

    public int getDurationInMonths() {
        return durationInMonths;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public void updateFrom(SharedPlanUpsertRequest request) {
        this.title = request.title();
        this.description = request.description();
        this.durationInMonths = request.durationInMonths();
        this.price = request.price();
    }
}
