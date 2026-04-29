package com.workshop.architecture.fitness.application.port.outbound;

import com.workshop.architecture.fitness.application.ActivateMembershipInput;
import com.workshop.architecture.fitness.domain.Customer;
import org.springframework.stereotype.Component;

public interface ForFindingCustomers {

    Customer findCustomerByIdOrThrow(ActivateMembershipInput input);
}
