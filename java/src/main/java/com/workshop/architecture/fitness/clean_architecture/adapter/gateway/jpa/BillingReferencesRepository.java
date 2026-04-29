package com.workshop.architecture.fitness.clean_architecture.adapter.gateway.jpa;

import com.workshop.architecture.fitness.clean_architecture.use_case.port.outbound.ForStoringBillingReferences;
import com.workshop.architecture.fitness.clean_architecture.entity.MembershipBillingReference;
import com.workshop.architecture.fitness.layered.infrastructure.MembershipBillingReferenceEntity;
import com.workshop.architecture.fitness.layered.infrastructure.MembershipBillingReferenceRepository;
import org.springframework.stereotype.Component;

@Component
public class BillingReferencesRepository implements ForStoringBillingReferences {

    private final MembershipBillingReferenceRepository billingReferenceRepository;

    public BillingReferencesRepository(MembershipBillingReferenceRepository billingReferenceRepository) {
        this.billingReferenceRepository = billingReferenceRepository;
    }

    @Override
    public MembershipBillingReference storeMembershipBillingReference(MembershipBillingReference billingReference) {
        var referenceEntity = new MembershipBillingReferenceEntity(
                billingReference.id(),
                billingReference.membershipId(),
                billingReference.externalInvoiceId(),
                billingReference.externalInvoiceReference(),
                billingReference.dueDate(),
                billingReference.status(),
                billingReference.createdAt(),
                billingReference.updatedAt()
        );

        var storedEntity = billingReferenceRepository.save(referenceEntity);

        return new MembershipBillingReference(
                storedEntity.getId(),
                storedEntity.getMembershipId(),
                storedEntity.getExternalInvoiceId(),
                storedEntity.getExternalInvoiceReference(),
                storedEntity.getDueDate(),
                storedEntity.getStatus(),
                storedEntity.getCreatedAt(),
                storedEntity.getUpdatedAt()
        );
    }
}
