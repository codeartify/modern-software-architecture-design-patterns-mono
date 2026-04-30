package com.workshop.architecture.fitness.managing_memberships.suspend_membership;

import com.workshop.architecture.fitness.managing_memberships.shared.MembershipBillingReferenceEntity;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipBillingReferenceRepository;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipEntity;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipRepository;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/api/memberships")
public class SuspendMembershipController {

    private final MembershipRepository membershipRepository;
    private final MembershipBillingReferenceRepository billingReferenceRepository;

    public SuspendMembershipController(
            MembershipRepository membershipRepository,
            MembershipBillingReferenceRepository billingReferenceRepository
    ) {
        this.membershipRepository = membershipRepository;
        this.billingReferenceRepository = billingReferenceRepository;
    }

    @PostMapping("/suspend-overdue")
    SuspendOverdueMembershipsResponse suspendOverdueMemberships(
            @RequestBody(required = false) SuspendOverdueMembershipsRequest request
    ) {
        Instant checkedAt = request == null || request.checkedAt() == null ? Instant.now() : request.checkedAt();
        LocalDate checkedAtDate = checkedAt.atZone(ZoneOffset.UTC).toLocalDate();
        List<MembershipEntity> memberships = membershipRepository.findAll();
        List<MembershipBillingReferenceEntity> openBillingReferences = billingReferenceRepository.findByStatus("OPEN");
        List<String> suspendedMembershipIds = new ArrayList<>();
        int checkedMemberships = 0;

        for (MembershipEntity membership : memberships) {
            if (!"ACTIVE".equals(membership.getStatus())) {
                continue;
            }

            checkedMemberships++;

            MembershipBillingReferenceEntity overdueBillingReference = openBillingReferences.stream()
                    .filter(billingReference -> membership.getId().equals(billingReference.getMembershipId()))
                    .filter(billingReference -> billingReference.getDueDate().isBefore(checkedAtDate))
                    .findFirst()
                    .orElse(null);

            if (overdueBillingReference == null) {
                continue;
            }

            if (!membership.isSuspendedForNonPayment()) {
                membership.suspendForNonPayment();
                membershipRepository.save(membership);
                suspendedMembershipIds.add(membership.getId().toString());
            }
        }

        return new SuspendOverdueMembershipsResponse(
                checkedAt,
                checkedMemberships,
                suspendedMembershipIds
        );
    }

}
