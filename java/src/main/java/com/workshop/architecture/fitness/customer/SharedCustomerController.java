package com.workshop.architecture.fitness.customer;

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
@RequestMapping("/api/shared/customers")
public class SharedCustomerController {

    private final SharedCustomerService service;

    public SharedCustomerController(SharedCustomerService service) {
        this.service = service;
    }

    @GetMapping
    List<SharedCustomerResponse> listCustomers() {
        return service.findAll();
    }

    @GetMapping("/{customerId}")
    SharedCustomerResponse getCustomer(@PathVariable UUID customerId) {
        return service.findById(customerId);
    }

    @PostMapping
    ResponseEntity<SharedCustomerResponse> createCustomer(@Valid @RequestBody SharedCustomerUpsertRequest request) {
        SharedCustomerResponse response = service.create(request);
        return ResponseEntity.created(URI.create("/api/shared/customers/" + response.id())).body(response);
    }

    @PutMapping("/{customerId}")
    SharedCustomerResponse updateCustomer(
            @PathVariable UUID customerId,
            @Valid @RequestBody SharedCustomerUpsertRequest request
    ) {
        return service.update(customerId, request);
    }

    @DeleteMapping("/{customerId}")
    ResponseEntity<Void> deleteCustomer(@PathVariable UUID customerId) {
        service.delete(customerId);
        return ResponseEntity.noContent().build();
    }
}
