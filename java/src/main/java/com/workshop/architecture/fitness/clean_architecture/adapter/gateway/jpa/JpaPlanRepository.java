package com.workshop.architecture.fitness.clean_architecture.adapter.gateway.jpa;

import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.ForFindingPlans;
import com.workshop.architecture.fitness.clean_architecture.entity.Plan;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.PlanNotFoundException;
import com.workshop.architecture.fitness.layered.infrastructure.PlanRepository;
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
        return new Plan(planId, planEntity.getPrice(), planEntity.getDurationInMonths(), planEntity.getTitle());
    }
}
