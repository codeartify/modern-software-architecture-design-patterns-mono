package com.workshop.architecture.fitness.membership.infrastructure;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface MembershipRepository extends JpaRepository<MembershipEntity, UUID> {
}
