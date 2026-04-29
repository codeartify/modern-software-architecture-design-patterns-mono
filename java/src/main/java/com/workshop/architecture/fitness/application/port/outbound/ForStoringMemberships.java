package com.workshop.architecture.fitness.application.port.outbound;

import com.workshop.architecture.fitness.domain.Membership;

public interface ForStoringMemberships {
    Membership storeMembership(Membership membership);
}
