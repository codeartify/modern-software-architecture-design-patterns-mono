package com.workshop.architecture.fitness.hexagon.inside.port.outbound;

import java.util.UUID;

public interface ForFindingCustomers {

    Customer findCustomerById(UUID customerId) throws CustomerNotFoundException;
}
