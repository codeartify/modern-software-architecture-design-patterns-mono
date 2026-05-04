package com.workshop.architecture.fitness.hexagon.outside.driver;

import com.workshop.architecture.fitness.hexagon.inside.port.inbound.ForActivatingMemberships;
import com.workshop.architecture.fitness.layered.infrastructure.MembershipEntity;
import com.workshop.architecture.fitness.layered.infrastructure.MembershipRepository;
import com.workshop.architecture.fitness.hexagon.inside.port.inbound.ActivateMembershipInput;
import jakarta.transaction.Transactional;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/memberships")
public class MembershipController {

    private final MembershipRepository membershipRepository;
    private final ForActivatingMemberships forActivatingMemberships;

    public MembershipController(
            MembershipRepository membershipRepository,
            ForActivatingMemberships forActivatingMemberships
    ) {
        this.membershipRepository = membershipRepository;
        this.forActivatingMemberships = forActivatingMemberships;
    }

    @GetMapping
    List<MembershipResponse> listMemberships() {
        return membershipRepository.findAll().stream()
                .map(MembershipController::fromEntity)
                .toList();
    }

    @GetMapping("/{membershipId}")
    MembershipResponse getMembership(@PathVariable String membershipId) {
        MembershipEntity membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        return fromEntity(membership);
    }

    @PostMapping("/activate")
    @Transactional
    ActivateMembershipResponse activateMembership(@Valid @RequestBody ActivateMembershipRequest request) {

        var input = new ActivateMembershipInput(request.customerId(), request.planId(), request.signedByCustodian());

        var result = forActivatingMemberships.activateMembership(input);
        
        return new ActivateMembershipResponse(
                result.membershipId(),
                result.customerId(),
                result.planId(),
                result.planPrice(),
                result.planDuration(),
                result.status(),
                result.startDate(),
                result.endDate(),
                result.invoiceId(),
                result.externalInvoiceId(),
                result.invoiceDueDate()

        );
    }

    public static MembershipResponse fromEntity(MembershipEntity entity) {
        return new MembershipResponse(
                entity.getId().toString(),
                entity.getCustomerId(),
                entity.getPlanId(),
                entity.getPlanPrice(),
                entity.getPlanDuration(),
                entity.getStatus(),
                entity.getReason(),
                entity.getStartDate(),
                entity.getEndDate()
        );
    }
}
