package com.workshop.architecture.fitness.hexagon.inside.port.outbound;

import java.util.UUID;

public interface ForFindingPlans {
    Plan findPlanById(UUID planId) throws PlanNotFoundException;
}
