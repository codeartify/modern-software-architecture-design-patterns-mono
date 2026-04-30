package com.workshop.architecture.fitness.membership.shared;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface MembershipBillingReferenceRepository
        extends JpaRepository<MembershipBillingReferenceEntity, UUID> {

    Optional<MembershipBillingReferenceEntity> findByExternalInvoiceId(String externalInvoiceId);

    Optional<MembershipBillingReferenceEntity> findByExternalInvoiceReference(
            String externalInvoiceReference
    );

    List<MembershipBillingReferenceEntity> findByMembershipId(UUID membershipId);

    List<MembershipBillingReferenceEntity> findByStatus(String status);
}
