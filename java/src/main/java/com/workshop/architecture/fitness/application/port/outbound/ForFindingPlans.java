package com.workshop.architecture.fitness.application.port.outbound;

import com.workshop.architecture.fitness.domain.Plan;

import java.util.UUID;

public interface ForFindingPlans {
    Plan findPlanById(UUID planId) throws PlanNotFoundException;
}
