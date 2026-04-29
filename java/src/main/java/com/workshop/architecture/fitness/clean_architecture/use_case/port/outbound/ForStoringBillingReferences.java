package com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound;

import com.workshop.architecture.fitness.clean_architecture.entity.MembershipBillingReference;

public interface ForStoringBillingReferences {
    MembershipBillingReference storeMembershipBillingReference(MembershipBillingReference billingReference);
}
