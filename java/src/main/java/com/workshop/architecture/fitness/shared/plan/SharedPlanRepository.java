package com.workshop.architecture.fitness.shared.plan;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SharedPlanRepository extends JpaRepository<SharedPlanEntity, UUID> {
}
