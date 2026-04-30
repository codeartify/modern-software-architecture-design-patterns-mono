package com.workshop.architecture.fitness.managing_memberships.cancel_membership;

import com.workshop.architecture.fitness.managing_memberships.shared.MembershipEntity;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipRepository;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.time.Instant;
import java.util.UUID;

@RestController
@RequestMapping("/api/memberships")
public class CancelMembershipController {

    private final MembershipRepository membershipRepository;

    public CancelMembershipController(
            MembershipRepository membershipRepository
    ) {
        this.membershipRepository = membershipRepository;
    }

    @PostMapping("/{membershipId}/cancel")
    CancelMembershipResponse cancelMembership(
            @PathVariable String membershipId,
            @RequestBody(required = false) CancelMembershipRequest request
    ) {
        MembershipEntity membership;
        Instant cancelledAt;
        String previousStatus;
        String reason;

        membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        if (membership.isCancelled()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Membership is already cancelled");
        }

        cancelledAt = request == null || request.cancelledAt() == null ? Instant.now() : request.cancelledAt();
        reason = request == null ? null : request.reason();
        previousStatus = membership.getStatus();

        membership.cancel(cancelledAt, reason);
        membership = membershipRepository.save(membership);

        return new CancelMembershipResponse(
                membership.getId().toString(),
                previousStatus,
                membership.getStatus(),
                membership.getCancelledAt(),
                membership.getCancellationReason(),
                "Membership cancelled"
        );
    }

}
