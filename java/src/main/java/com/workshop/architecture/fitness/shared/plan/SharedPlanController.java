package com.workshop.architecture.fitness.shared.plan;

import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/shared/plans")
public class SharedPlanController {

    private final SharedPlanService service;

    public SharedPlanController(SharedPlanService service) {
        this.service = service;
    }

    @GetMapping
    List<SharedPlanResponse> listPlans() {
        return service.findAll();
    }

    @GetMapping("/{planId}")
    SharedPlanResponse getPlan(@PathVariable UUID planId) {
        return service.findById(planId);
    }

    @PostMapping
    ResponseEntity<SharedPlanResponse> createPlan(@Valid @RequestBody SharedPlanUpsertRequest request) {
        SharedPlanResponse response = service.create(request);
        return ResponseEntity.created(URI.create("/api/shared/plans/" + response.id())).body(response);
    }

    @PutMapping("/{planId}")
    SharedPlanResponse updatePlan(
            @PathVariable UUID planId,
            @Valid @RequestBody SharedPlanUpsertRequest request
    ) {
        return service.update(planId, request);
    }

    @DeleteMapping("/{planId}")
    ResponseEntity<Void> deletePlan(@PathVariable UUID planId) {
        service.delete(planId);
        return ResponseEntity.noContent().build();
    }
}
