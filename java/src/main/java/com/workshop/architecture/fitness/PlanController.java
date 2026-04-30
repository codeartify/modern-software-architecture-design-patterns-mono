package com.workshop.architecture.fitness;

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
