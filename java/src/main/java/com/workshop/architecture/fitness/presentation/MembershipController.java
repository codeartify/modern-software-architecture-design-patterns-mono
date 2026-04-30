package com.workshop.architecture.fitness.presentation;

import com.workshop.architecture.fitness.business.application.ActivateMembershipInput;
import com.workshop.architecture.fitness.business.application.MembershipService;
import com.workshop.architecture.fitness.infrastructure.MembershipEntity;
import com.workshop.architecture.fitness.infrastructure.MembershipRepository;
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

        var input = new ActivateMembershipInput(request.customerId(), request.planId(), request.signedByCustodian());

        var result = membershipService.activateMembership(input);
        
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
