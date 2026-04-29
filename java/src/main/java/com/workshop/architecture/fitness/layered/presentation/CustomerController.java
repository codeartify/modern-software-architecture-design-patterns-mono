package com.workshop.architecture.fitness.layered.presentation;

import com.workshop.architecture.fitness.layered.business.CustomerService;
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
@RequestMapping("/api/customers")
public class CustomerController {

    private final CustomerService service;

    public CustomerController(CustomerService service) {
        this.service = service;
    }

    @GetMapping
    List<CustomerResponse> listCustomers() {
        return service.findAll();
    }

    @GetMapping("/{customerId}")
    CustomerResponse getCustomer(@PathVariable UUID customerId) {
        return service.findById(customerId);
    }

    @PostMapping
    ResponseEntity<CustomerResponse> createCustomer(@Valid @RequestBody CustomerUpsertRequest request) {
        CustomerResponse response = service.create(request);
        return ResponseEntity.created(URI.create("/api/customers/" + response.id())).body(response);
    }

    @PutMapping("/{customerId}")
    CustomerResponse updateCustomer(
            @PathVariable UUID customerId,
            @Valid @RequestBody CustomerUpsertRequest request
    ) {
        return service.update(customerId, request);
    }

    @DeleteMapping("/{customerId}")
    ResponseEntity<Void> deleteCustomer(@PathVariable UUID customerId) {
        service.delete(customerId);
        return ResponseEntity.noContent().build();
    }
}
