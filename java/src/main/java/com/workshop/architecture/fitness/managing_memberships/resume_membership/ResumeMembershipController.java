package com.workshop.architecture.fitness.managing_memberships.resume_membership;

import com.workshop.architecture.fitness.managing_memberships.shared.MembershipEntity;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipRepository;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.time.Instant;
import java.time.LocalDate;
import java.util.UUID;

@RestController
@RequestMapping("/api/memberships")
public class ResumeMembershipController {

    private final MembershipRepository membershipRepository;

    public ResumeMembershipController(
            MembershipRepository membershipRepository
    ) {
        this.membershipRepository = membershipRepository;
    }

    @PostMapping("/{membershipId}/resume")
    ResumeMembershipResponse resumeMembership(
            @PathVariable String membershipId,
            @RequestBody(required = false) ResumeMembershipRequest request
    ) {
        MembershipEntity membership;
        Instant resumedAt;
        String previousStatus;
        LocalDate previousPauseStartDate;
        LocalDate previousPauseEndDate;
        String reason;

        membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        if (!membership.isPaused()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Only paused memberships can be resumed");
        }

        if (membership.getEndDate().isBefore(LocalDate.now())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Expired memberships cannot be resumed");
        }

        resumedAt = request == null || request.resumedAt() == null ? Instant.now() : request.resumedAt();
        reason = request == null ? null : request.reason();
        previousStatus = membership.getStatus();
        previousPauseStartDate = membership.getPauseStartDate();
        previousPauseEndDate = membership.getPauseEndDate();

        membership.resumeAfterPause();
        membership = membershipRepository.save(membership);

        return new ResumeMembershipResponse(
                membership.getId().toString(),
                previousStatus,
                membership.getStatus(),
                resumedAt,
                previousPauseStartDate,
                previousPauseEndDate,
                membership.getEndDate(),
                reason,
                "Membership resumed"
        );
    }

}
