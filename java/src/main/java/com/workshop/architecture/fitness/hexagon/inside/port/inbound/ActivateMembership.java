package com.workshop.architecture.fitness.hexagon.inside.port.inbound;

import jakarta.transaction.Transactional;

public interface ActivateMembership {
    @Transactional
    ActivateMembershipResult activateMembership(ActivateMembershipInput input);
}
