package com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound;

import com.workshop.architecture.fitness.clean_architecture.entity.Plan;

import java.util.UUID;

public interface ForFindingPlans {
    Plan findPlanById(UUID planId) throws PlanNotFoundException;
}
