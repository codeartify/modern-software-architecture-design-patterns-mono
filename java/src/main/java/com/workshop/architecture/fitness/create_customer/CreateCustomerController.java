package com.workshop.architecture.fitness.create_customer;

import com.workshop.architecture.fitness.shared.CustomerEntity;
import com.workshop.architecture.fitness.shared.CustomerRepository;
import com.workshop.architecture.fitness.shared.CustomerResponse;
import com.workshop.architecture.fitness.shared.CustomerUpsertRequest;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/customers")
public class CreateCustomerController {

    private final CustomerRepository customerRepository;

    public CreateCustomerController(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    @PostMapping
    ResponseEntity<CustomerResponse> createCustomer(@Valid @RequestBody CustomerUpsertRequest request) {
        CustomerEntity customer = new CustomerEntity(
                UUID.randomUUID(),
                request.name(),
                request.dateOfBirth(),
                request.emailAddress()
        );

        CustomerResponse response = CustomerResponse.fromEntity(customerRepository.save(customer));
        return ResponseEntity.created(URI.create("/api/customers/" + response.id())).body(response);
    }
}
