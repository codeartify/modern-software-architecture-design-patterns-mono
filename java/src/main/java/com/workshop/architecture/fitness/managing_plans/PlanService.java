package com.workshop.architecture.fitness.managing_plans;

import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class PlanService {

    private final PlanRepository repository;

    public PlanService(PlanRepository repository) {
        this.repository = repository;
    }

    public List<PlanResponse> findAll() {
        return repository.findAll().stream()
                .sorted(Comparator.comparing(PlanEntity::getTitle))
                .map(PlanResponse::fromEntity)
                .toList();
    }

    public PlanResponse findById(UUID planId) {
        return PlanResponse.fromEntity(load(planId));
    }

    public PlanResponse create(PlanUpsertRequest request) {
        PlanEntity entity = new PlanEntity(
                UUID.randomUUID(),
                request.title(),
                request.description(),
                request.durationInMonths(),
                request.price()
        );
        return PlanResponse.fromEntity(repository.save(entity));
    }

    public PlanResponse update(UUID planId, PlanUpsertRequest request) {
        PlanEntity entity = load(planId);
        entity.updateFrom(request);
        return PlanResponse.fromEntity(repository.save(entity));
    }

    public void delete(UUID planId) {
        PlanEntity entity = load(planId);
        repository.delete(entity);
    }

    private PlanEntity load(UUID planId) {
        return repository.findById(planId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Plan %s was not found".formatted(planId)
                ));
    }
}
