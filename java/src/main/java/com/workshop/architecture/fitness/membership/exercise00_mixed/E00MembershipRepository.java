package com.workshop.architecture.fitness.membership.exercise00_mixed;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface E00MembershipRepository extends JpaRepository<com.workshop.architecture.fitness.membership.exercise00_mixed.E00MembershipEntity, UUID> {
}
