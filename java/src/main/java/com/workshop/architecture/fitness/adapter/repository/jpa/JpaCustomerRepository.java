package com.workshop.architecture.fitness.adapter.repository.jpa;

import com.workshop.architecture.fitness.application.ActivateMembershipInput;
import com.workshop.architecture.fitness.application.port.outbound.ForFindingCustomers;
import com.workshop.architecture.fitness.domain.Customer;
import com.workshop.architecture.fitness.infrastructure.CustomerNotFoundException;
import com.workshop.architecture.fitness.infrastructure.CustomerRepository;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
public class JpaCustomerRepository implements ForFindingCustomers {

    private final CustomerRepository customerRepository;

    public JpaCustomerRepository(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    public Customer findCustomerByIdOrThrow(ActivateMembershipInput input) {
        var customerEntity = customerRepository.findById(UUID.fromString(input.customerId()))
                .orElseThrow(() -> new CustomerNotFoundException(
                        "Customer %s was not found".formatted(input.customerId())
                ));

        return new Customer(customerEntity.getDateOfBirth(), customerEntity.getEmailAddress());
    }
}
