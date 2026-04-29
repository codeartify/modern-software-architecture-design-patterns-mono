package com.workshop.architecture.fitness.application.port.outbound;

import com.workshop.architecture.fitness.domain.MembershipBillingReference;

public interface ForStoringBillingReferences {
    MembershipBillingReference storeMembershipBillingReference(MembershipBillingReference billingReference);
}
