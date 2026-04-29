package com.workshop.architecture.fitness.inside.port.inbound;

import jakarta.transaction.Transactional;

public interface ActivateMembership {
    @Transactional
    ActivateMembershipResult activateMembership(ActivateMembershipInput input);
}
