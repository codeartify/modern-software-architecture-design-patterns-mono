package com.workshop.architecture.fitness.adapter.repository.jpa;

import com.workshop.architecture.fitness.application.port.outbound.ForFindingPlans;
import com.workshop.architecture.fitness.domain.Plan;
import com.workshop.architecture.fitness.application.port.outbound.PlanNotFoundException;
import com.workshop.architecture.fitness.infrastructure.PlanRepository;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
public class JpaPlanRepository implements ForFindingPlans {
    private final PlanRepository planRepository;

    public JpaPlanRepository(PlanRepository planRepository) {
        this.planRepository = planRepository;
    }
    
    public Plan findPlanById(UUID planId) throws PlanNotFoundException {
        var planEntity = planRepository.findById(planId)
                .orElseThrow(() -> new PlanNotFoundException(
                        "Plan %s was not found".formatted(planId.toString())
                ));
        return new Plan(planEntity.getPrice(), planEntity.getDurationInMonths(), planEntity.getTitle());
    }
}
