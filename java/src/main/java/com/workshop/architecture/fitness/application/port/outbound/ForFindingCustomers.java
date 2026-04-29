package com.workshop.architecture.fitness.application.port.outbound;

import com.workshop.architecture.fitness.domain.Customer;

import java.util.UUID;

public interface ForFindingCustomers {

    Customer findCustomerById(UUID customerId) throws CustomerNotFoundException;
}
