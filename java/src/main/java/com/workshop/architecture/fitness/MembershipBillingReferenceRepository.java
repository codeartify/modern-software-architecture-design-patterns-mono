package com.workshop.architecture.fitness;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MembershipBillingReferenceRepository
        extends JpaRepository<MembershipBillingReferenceEntity, UUID> {

    Optional<MembershipBillingReferenceEntity> findByExternalInvoiceId(String externalInvoiceId);

    Optional<MembershipBillingReferenceEntity> findByExternalInvoiceReference(
            String externalInvoiceReference
    );

    List<MembershipBillingReferenceEntity> findByMembershipId(UUID membershipId);

    List<MembershipBillingReferenceEntity> findByStatus(String status);
}
