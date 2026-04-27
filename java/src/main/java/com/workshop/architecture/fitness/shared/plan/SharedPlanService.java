package com.workshop.architecture.fitness.shared.plan;

import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class SharedPlanService {

    private final SharedPlanRepository repository;

    public SharedPlanService(SharedPlanRepository repository) {
        this.repository = repository;
    }

    public List<SharedPlanResponse> findAll() {
        return repository.findAll().stream()
                .map(SharedPlanResponse::fromEntity)
                .toList();
    }

    public SharedPlanResponse findById(UUID planId) {
        return SharedPlanResponse.fromEntity(load(planId));
    }

    public SharedPlanResponse create(SharedPlanUpsertRequest request) {
        SharedPlanEntity entity = new SharedPlanEntity(
                UUID.randomUUID(),
                request.title(),
                request.description(),
                request.durationInMonths(),
                request.price()
        );
        return SharedPlanResponse.fromEntity(repository.save(entity));
    }

    public SharedPlanResponse update(UUID planId, SharedPlanUpsertRequest request) {
        SharedPlanEntity entity = load(planId);
        entity.updateFrom(request);
        return SharedPlanResponse.fromEntity(repository.save(entity));
    }

    public void delete(UUID planId) {
        SharedPlanEntity entity = load(planId);
        repository.delete(entity);
    }

    private SharedPlanEntity load(UUID planId) {
        return repository.findById(planId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Plan %s was not found".formatted(planId)
                ));
    }
}
