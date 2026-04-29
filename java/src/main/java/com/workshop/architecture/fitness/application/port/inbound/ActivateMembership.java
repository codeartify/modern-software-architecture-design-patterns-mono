package com.workshop.architecture.fitness.application.port.inbound;

import com.workshop.architecture.fitness.application.ActivateMembershipInput;
import com.workshop.architecture.fitness.application.ActivateMembershipResult;
import jakarta.transaction.Transactional;

public interface ActivateMembership {
    @Transactional
    ActivateMembershipResult activateMembership(ActivateMembershipInput input);
}
