package com.workshop.architecture.fitness.membership.exercise00_mixed;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;

public interface E00MembershipBillingReferenceRepository
        extends JpaRepository<E00MembershipBillingReferenceEntity, UUID> {

    Optional<E00MembershipBillingReferenceEntity> findByExternalInvoiceId(String externalInvoiceId);

    Optional<E00MembershipBillingReferenceEntity> findByExternalInvoiceReference(
            String externalInvoiceReference
    );

    List<E00MembershipBillingReferenceEntity> findByMembershipId(UUID membershipId);

    List<E00MembershipBillingReferenceEntity> findByStatus(String status);
}
