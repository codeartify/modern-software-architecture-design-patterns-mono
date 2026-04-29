package com.workshop.architecture.fitness.clean_architecture.adapter.gateway.jpa;

import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.ForStoringMemberships;
import com.workshop.architecture.fitness.clean_architecture.entity.Membership;
import com.workshop.architecture.fitness.layered.infrastructure.MembershipEntity;
import com.workshop.architecture.fitness.layered.infrastructure.MembershipRepository;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
public class JpaMembershipRepository implements ForStoringMemberships {
    private final MembershipRepository membershipRepository;

    public JpaMembershipRepository(MembershipRepository membershipRepository) {
        this.membershipRepository = membershipRepository;
    }

    @Override
    public Membership storeMembership(Membership membership) {
        var entity = new MembershipEntity(
                membership.id(),
                membership.customerId().toString(),
                membership.planId().toString(),
                membership.planPrice(),
                membership.planDurationInMonths(),
                membership.status(),
                membership.statusReason(),
                membership.startDate(),
                membership.endDate()
        );

        var storedEntity = membershipRepository.save(entity);

        return new Membership(
                storedEntity.getId(),
                UUID.fromString(storedEntity.getCustomerId()),
                UUID.fromString(storedEntity.getPlanId()),
                storedEntity.getPlanPrice(),
                storedEntity.getPlanDuration(),
                storedEntity.getStatus(),
                storedEntity.getReason(),
                storedEntity.getStartDate(),
                storedEntity.getEndDate()
        );
    }
}
