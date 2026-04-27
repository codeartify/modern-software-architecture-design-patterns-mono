package com.workshop.architecture.fitness.customer;

import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class SharedCustomerService {

    private final SharedCustomerRepository repository;

    public SharedCustomerService(SharedCustomerRepository repository) {
        this.repository = repository;
    }

    public List<SharedCustomerResponse> findAll() {
        return repository.findAll().stream()
                .map(SharedCustomerResponse::fromEntity)
                .toList();
    }

    public SharedCustomerResponse findById(UUID customerId) {
        return SharedCustomerResponse.fromEntity(load(customerId));
    }

    public SharedCustomerResponse create(SharedCustomerUpsertRequest request) {
        SharedCustomerEntity entity = new SharedCustomerEntity(
                UUID.randomUUID(),
                request.name(),
                request.dateOfBirth(),
                request.emailAddress()
        );
        return SharedCustomerResponse.fromEntity(repository.save(entity));
    }

    public SharedCustomerResponse update(UUID customerId, SharedCustomerUpsertRequest request) {
        SharedCustomerEntity entity = load(customerId);
        entity.updateFrom(request);
        return SharedCustomerResponse.fromEntity(repository.save(entity));
    }

    public void delete(UUID customerId) {
        SharedCustomerEntity entity = load(customerId);
        repository.delete(entity);
    }

    private SharedCustomerEntity load(UUID customerId) {
        return repository.findById(customerId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Customer %s was not found".formatted(customerId)
                ));
    }
}
