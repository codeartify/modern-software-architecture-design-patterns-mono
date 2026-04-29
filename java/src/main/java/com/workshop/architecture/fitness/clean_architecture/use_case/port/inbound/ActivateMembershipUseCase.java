package com.workshop.architecture.fitness.clean_architecture.use_case.port.inbound;

import jakarta.transaction.Transactional;

public interface ActivateMembershipUseCase {
    @Transactional
    ActivateMembershipResult activateMembership(ActivateMembershipInput input);
}
