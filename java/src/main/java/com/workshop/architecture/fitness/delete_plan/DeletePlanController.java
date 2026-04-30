package com.workshop.architecture.fitness.delete_plan;

import com.workshop.architecture.fitness.shared.PlanEntity;
import com.workshop.architecture.fitness.shared.PlanRepository;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/plans")
public class DeletePlanController {

    private final PlanRepository planRepository;

    public DeletePlanController(PlanRepository planRepository) {
        this.planRepository = planRepository;
    }

    @DeleteMapping("/{planId}")
    ResponseEntity<Void> deletePlan(@PathVariable UUID planId) {
        PlanEntity plan = planRepository.findById(planId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Plan %s was not found".formatted(planId)
                ));

        planRepository.delete(plan);
        return ResponseEntity.noContent().build();
    }
}
