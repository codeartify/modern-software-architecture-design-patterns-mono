package com.workshop.architecture.fitness.clean_architecture.adapter.gateway.jpa;

import com.workshop.architecture.fitness.clean_architecture.entity.CustomerId;
import com.workshop.architecture.fitness.clean_architecture.entity.Duration;
import com.workshop.architecture.fitness.clean_architecture.entity.Membership;
import com.workshop.architecture.fitness.clean_architecture.entity.MembershipId;
import com.workshop.architecture.fitness.clean_architecture.entity.MembershipStatus;
import com.workshop.architecture.fitness.clean_architecture.entity.MembershipStatusValue;
import com.workshop.architecture.fitness.clean_architecture.entity.PlanDetails;
import com.workshop.architecture.fitness.clean_architecture.entity.PlanId;
import com.workshop.architecture.fitness.clean_architecture.entity.Price;
import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.ForStoringMemberships;
import com.workshop.architecture.fitness.layered.infrastructure.MembershipEntity;
import com.workshop.architecture.fitness.layered.infrastructure.MembershipRepository;
import java.util.UUID;
import org.springframework.stereotype.Component;

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
                new MembershipId(storedEntity.getId()),
                new CustomerId(UUID.fromString(storedEntity.getCustomerId())),
                new MembershipStatus(
                        MembershipStatusValue.valueOf(storedEntity.getStatus().toUpperCase()),
                        storedEntity.getReason()
                ),
                new PlanDetails(
                        new PlanId(UUID.fromString(storedEntity.getPlanId())),
                        new Price(storedEntity.getPlanPrice()),
                        new Duration(storedEntity.getStartDate(), storedEntity.getEndDate())
                )
        );
    }
}
