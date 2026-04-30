package com.workshop.architecture.fitness.update_plan;

import com.workshop.architecture.fitness.shared.PlanEntity;
import com.workshop.architecture.fitness.shared.PlanRepository;
import com.workshop.architecture.fitness.shared.PlanResponse;
import com.workshop.architecture.fitness.shared.PlanUpsertRequest;
import jakarta.validation.Valid;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/plans")
public class UpdatePlanController {

    private final PlanRepository planRepository;

    public UpdatePlanController(PlanRepository planRepository) {
        this.planRepository = planRepository;
    }

    @PutMapping("/{planId}")
    PlanResponse updatePlan(
            @PathVariable UUID planId,
            @Valid @RequestBody PlanUpsertRequest request
    ) {
        PlanEntity plan = planRepository.findById(planId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Plan %s was not found".formatted(planId)
                ));

        plan.updateFrom(request);
        return PlanResponse.fromEntity(planRepository.save(plan));
    }
}
