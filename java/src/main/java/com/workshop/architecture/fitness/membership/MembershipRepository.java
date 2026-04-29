package com.workshop.architecture.fitness.membership;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface MembershipRepository extends JpaRepository<com.workshop.architecture.fitness.membership.MembershipEntity, UUID> {
}
