package com.workshop.architecture.fitness.managing_customers;

import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class CustomerService {

    private final CustomerRepository repository;

    public CustomerService(CustomerRepository repository) {
        this.repository = repository;
    }

    public List<CustomerResponse> findAll() {
        return repository.findAll().stream()
                .sorted(Comparator.comparing(CustomerEntity::getName))
                .map(CustomerResponse::fromEntity)
                .toList();
    }

    public CustomerResponse findById(UUID customerId) {
        return CustomerResponse.fromEntity(load(customerId));
    }

    public CustomerResponse create(CustomerUpsertRequest request) {
        CustomerEntity entity = new CustomerEntity(
                UUID.randomUUID(),
                request.name(),
                request.dateOfBirth(),
                request.emailAddress()
        );
        return CustomerResponse.fromEntity(repository.save(entity));
    }

    public CustomerResponse update(UUID customerId, CustomerUpsertRequest request) {
        CustomerEntity entity = load(customerId);
        entity.updateFrom(request);
        return CustomerResponse.fromEntity(repository.save(entity));
    }

    public void delete(UUID customerId) {
        CustomerEntity entity = load(customerId);
        repository.delete(entity);
    }

    private CustomerEntity load(UUID customerId) {
        return repository.findById(customerId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Customer %s was not found".formatted(customerId)
                ));
    }
}
