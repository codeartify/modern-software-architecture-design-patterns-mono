package com.workshop.architecture.fitness.plan;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PlanRepository extends JpaRepository<PlanEntity, UUID> {
}
