package com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound;

import com.workshop.architecture.fitness.clean_architecture.entity.Membership;

public interface ForStoringMemberships {
    Membership storeMembership(Membership membership);
}
