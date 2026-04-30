package com.workshop.architecture.fitness.pause_membership;

import com.workshop.architecture.fitness.shared.MembershipEntity;
import com.workshop.architecture.fitness.shared.MembershipRepository;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDate;
import java.util.UUID;

@RestController
@RequestMapping("/api/memberships")
public class PauseMembershipController {

    private final MembershipRepository membershipRepository;

    public PauseMembershipController(MembershipRepository membershipRepository) {
        this.membershipRepository = membershipRepository;
    }

    @PostMapping("/{membershipId}/pause")
    PauseMembershipResponse pauseMembership(
            @PathVariable String membershipId,
            @RequestBody PauseMembershipRequest request
    ) {
        MembershipEntity membership;
        String previousStatus;
        LocalDate previousEndDate;

        if (request.pauseStartDate() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "pauseStartDate is required");
        }

        if (request.pauseEndDate() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "pauseEndDate is required");
        }

        if (request.pauseEndDate().isBefore(request.pauseStartDate())) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "pauseEndDate must not be before pauseStartDate"
            );
        }

        membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        if (!membership.isActive()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Only active memberships can be paused");
        }

        if (membership.getEndDate().isBefore(LocalDate.now())) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Expired memberships cannot be paused");
        }

        previousStatus = membership.getStatus();
        previousEndDate = membership.getEndDate();

        membership.pause(request.pauseStartDate(), request.pauseEndDate(), request.reason());
        membership = membershipRepository.save(membership);

        return new PauseMembershipResponse(
                membership.getId().toString(),
                previousStatus,
                membership.getStatus(),
                membership.getPauseStartDate(),
                membership.getPauseEndDate(),
                previousEndDate,
                membership.getEndDate(),
                membership.getPauseReason(),
                "Membership paused"
        );
    }

}
