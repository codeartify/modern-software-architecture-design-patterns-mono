package com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound;

import com.workshop.architecture.fitness.clean_architecture.entity.Customer;

import java.util.UUID;

public interface ForFindingCustomers {

    Customer findCustomerById(UUID customerId) throws CustomerNotFoundException;
}
