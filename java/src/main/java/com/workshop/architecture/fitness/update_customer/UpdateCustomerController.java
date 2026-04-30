package com.workshop.architecture.fitness.update_customer;

import com.workshop.architecture.fitness.shared.CustomerEntity;
import com.workshop.architecture.fitness.shared.CustomerRepository;
import com.workshop.architecture.fitness.shared.CustomerResponse;
import com.workshop.architecture.fitness.shared.CustomerUpsertRequest;
import jakarta.validation.Valid;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/customers")
public class UpdateCustomerController {

    private final CustomerRepository customerRepository;

    public UpdateCustomerController(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    @PutMapping("/{customerId}")
    CustomerResponse updateCustomer(
            @PathVariable UUID customerId,
            @Valid @RequestBody CustomerUpsertRequest request
    ) {
        CustomerEntity customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Customer %s was not found".formatted(customerId)
                ));

        customer.updateFrom(request);
        return CustomerResponse.fromEntity(customerRepository.save(customer));
    }
}
