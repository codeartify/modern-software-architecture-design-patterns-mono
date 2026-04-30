package com.workshop.architecture.fitness.create_plan;

import com.workshop.architecture.fitness.shared.PlanEntity;
import com.workshop.architecture.fitness.shared.PlanRepository;
import com.workshop.architecture.fitness.shared.PlanResponse;
import com.workshop.architecture.fitness.shared.PlanUpsertRequest;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/plans")
public class CreatePlanController {

    private final PlanRepository planRepository;

    public CreatePlanController(PlanRepository planRepository) {
        this.planRepository = planRepository;
    }

    @PostMapping
    ResponseEntity<PlanResponse> createPlan(@Valid @RequestBody PlanUpsertRequest request) {
        PlanEntity plan = new PlanEntity(
                UUID.randomUUID(),
                request.title(),
                request.description(),
                request.durationInMonths(),
                request.price()
        );

        PlanResponse response = PlanResponse.fromEntity(planRepository.save(plan));
        return ResponseEntity.created(URI.create("/api/plans/" + response.id())).body(response);
    }
}
