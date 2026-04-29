package com.workshop.architecture.fitness.clean_architecture.adapter.gateway.jpa;

import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.ForFindingCustomers;
import com.workshop.architecture.fitness.clean_architecture.entity.Customer;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.CustomerNotFoundException;
import com.workshop.architecture.fitness.layered.infrastructure.CustomerRepository;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
public class JpaCustomerRepository implements ForFindingCustomers {

    private final CustomerRepository customerRepository;

    public JpaCustomerRepository(CustomerRepository customerRepository) {
        this.customerRepository = customerRepository;
    }

    public Customer findCustomerById(UUID customerId) throws CustomerNotFoundException{
        var customerEntity = customerRepository.findById(customerId)
                .orElseThrow(() -> new CustomerNotFoundException(
                        "Customer %s was not found".formatted(customerId.toString())
                ));

        return new Customer(customerEntity.getId(), customerEntity.getDateOfBirth(), customerEntity.getEmailAddress());
    }
}
