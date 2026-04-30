package com.workshop.architecture.fitness.managing_memberships.get_membership;

import com.workshop.architecture.fitness.managing_memberships.shared.MembershipEntity;
import com.workshop.architecture.fitness.managing_memberships.shared.MembershipRepository;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.util.UUID;

@RestController
@RequestMapping("/api/memberships")
public class GetMembershipController {

    private final MembershipRepository membershipRepository;

    public GetMembershipController(MembershipRepository membershipRepository) {
        this.membershipRepository = membershipRepository;
    }


    @GetMapping("/{membershipId}")
    GetMembershipResponse getMembership(@PathVariable String membershipId) {
        MembershipEntity membership = membershipRepository.findById(UUID.fromString(membershipId))
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Membership %s was not found".formatted(membershipId)
                ));

        return GetMembershipResponse.fromEntity(membership);
    }

}
