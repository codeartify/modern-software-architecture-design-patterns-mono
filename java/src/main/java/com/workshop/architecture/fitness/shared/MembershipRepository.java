package com.workshop.architecture.fitness.shared;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface MembershipRepository extends JpaRepository<MembershipEntity, UUID> {
}
