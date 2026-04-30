package com.workshop.architecture.fitness.layered.presentation;

import com.workshop.architecture.fitness.layered.business.PlanService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.net.URI;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/plans")
public class PlanController {

    private final PlanService service;

    public PlanController(PlanService service) {
        this.service = service;
    }

    @GetMapping
    List<PlanResponse> listPlans() {
        return service.findAll();
    }

    @GetMapping("/{planId}")
    PlanResponse getPlan(@PathVariable UUID planId) {
        return service.findById(planId);
    }

    @PostMapping
    ResponseEntity<PlanResponse> createPlan(@Valid @RequestBody PlanUpsertRequest request) {
        PlanResponse response = service.create(request);
        return ResponseEntity.created(URI.create("/api/plans/" + response.id())).body(response);
    }

    @PutMapping("/{planId}")
    PlanResponse updatePlan(
            @PathVariable UUID planId,
            @Valid @RequestBody PlanUpsertRequest request
    ) {
        return service.update(planId, request);
    }

    @DeleteMapping("/{planId}")
    ResponseEntity<Void> deletePlan(@PathVariable UUID planId) {
        service.delete(planId);
        return ResponseEntity.noContent().build();
    }
}
