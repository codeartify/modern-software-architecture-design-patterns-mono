package com.workshop.architecture.fitness.get_plan;

import com.workshop.architecture.fitness.shared.PlanRepository;
import com.workshop.architecture.fitness.shared.PlanResponse;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/plans")
public class GetPlanController {

    private final PlanRepository planRepository;

    public GetPlanController(PlanRepository planRepository) {
        this.planRepository = planRepository;
    }

    @GetMapping("/{planId}")
    PlanResponse getPlan(@PathVariable UUID planId) {
        return planRepository.findById(planId)
                .map(PlanResponse::fromEntity)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Plan %s was not found".formatted(planId)
                ));
    }
}
