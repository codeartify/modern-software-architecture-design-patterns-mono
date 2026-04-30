package com.workshop.architecture.fitness.delete_customer;

import com.workshop.architecture.fitness.shared.CustomerEntity;
import com.workshop.architecture.fitness.shared.CustomerRepository;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/customers")
public class DeleteCustomerController {

    private final CustomerRepository customerRepository;

    public DeleteCustomerController(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    @DeleteMapping("/{customerId}")
    ResponseEntity<Void> deleteCustomer(@PathVariable UUID customerId) {
        CustomerEntity customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Customer %s was not found".formatted(customerId)
                ));

        customerRepository.delete(customer);
        return ResponseEntity.noContent().build();
    }
}
