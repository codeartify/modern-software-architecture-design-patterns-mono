package com.workshop.architecture.fitness.managing_memberships.list_memberships;

import com.workshop.architecture.fitness.managing_memberships.shared.MembershipRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/memberships")
public class ListMembershipController {

    private final MembershipRepository membershipRepository;

    public ListMembershipController(
            MembershipRepository membershipRepository
    ) {
        this.membershipRepository = membershipRepository;
    }

    @GetMapping
    List<ListMembershipResponse> listMemberships() {
        return membershipRepository.findAll().stream()
                .map(ListMembershipResponse::fromEntity)
                .toList();
    }

}
