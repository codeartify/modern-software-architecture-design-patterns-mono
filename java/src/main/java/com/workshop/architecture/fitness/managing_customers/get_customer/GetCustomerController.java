package com.workshop.architecture.fitness.managing_customers.get_customer;

import com.workshop.architecture.fitness.managing_customers.shared.CustomerRepository;
import com.workshop.architecture.fitness.managing_customers.shared.CustomerResponse;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/customers")
public class GetCustomerController {

    private final CustomerRepository customerRepository;

    public GetCustomerController(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    @GetMapping("/{customerId}")
    CustomerResponse getCustomer(@PathVariable UUID customerId) {
        return customerRepository.findById(customerId)
                .map(CustomerResponse::fromEntity)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Customer %s was not found".formatted(customerId)
                ));
    }
}
