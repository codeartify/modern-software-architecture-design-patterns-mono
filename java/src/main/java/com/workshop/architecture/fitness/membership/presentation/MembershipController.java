package com.workshop.architecture.fitness.membership.presentation;

import com.workshop.architecture.fitness.membership.business.ActivateMembershipInput;
import com.workshop.architecture.fitness.membership.business.MembershipService;
import com.workshop.architecture.fitness.membership.infrastructure.MembershipEntity;
import com.workshop.architecture.fitness.membership.infrastructure.MembershipRepository;
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
    private final MembershipService membershipService;

    public MembershipController(
            MembershipRepository membershipRepository,
            MembershipService membershipService
    ) {
        this.membershipRepository = membershipRepository;
        this.membershipService = membershipService;
    }

    @GetMapping
    List<MembershipResponse> listMemberships() {
        return membershipRepository.findAll().stream()
                .map(MembershipResponse::fromEntity)
                .toList();
    }

    @GetMapping("/{membershipId}")
    MembershipResponse getMembership(@PathVariable String membershipId) {
        MembershipEntity membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        return MembershipResponse.fromEntity(membership);
    }

    @PostMapping("/activate")
    @Transactional
    ActivateMembershipResponse activateMembership(@Valid @RequestBody ActivateMembershipRequest request) {

        var result = membershipService.activateMembership(new ActivateMembershipInput(request.customerId(), request.planId(), request.signedByCustodian()));
        
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

}
