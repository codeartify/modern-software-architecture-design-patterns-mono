import uuid

from workshop_api.fitness.hexagon.inside.port.outbound.for_storing_billing_references import (
    ForStoringBillingReferences,
)
from workshop_api.fitness.hexagon.inside.port.outbound.membership_billing_reference import (
    MembershipBillingReference,
)
from workshop_api.fitness.layered.infrastructure.membership_billing_reference_repository import (
    MembershipBillingReferenceRepository,
)
from workshop_api.fitness.layered.infrastructure.membership_entity import (
    MembershipBillingReferenceOrmModel,
)


class SqlAlchemyMembershipBillingReferencesRepository(ForStoringBillingReferences):
    def __init__(
        self,
        billing_reference_repository: MembershipBillingReferenceRepository,
    ) -> None:
        self.billing_reference_repository = billing_reference_repository

    def store_membership_billing_reference(
        self,
        billing_reference: MembershipBillingReference,
    ) -> MembershipBillingReference:
        reference_entity = MembershipBillingReferenceOrmModel(
            id=str(billing_reference.id),
            membership_id=str(billing_reference.membership_id),
            external_invoice_id=billing_reference.external_invoice_id,
            external_invoice_reference=billing_reference.external_invoice_reference,
            due_date=billing_reference.due_date,
            status=billing_reference.status,
            created_at=billing_reference.created_at,
            updated_at=billing_reference.updated_at,
        )

        stored_entity = self.billing_reference_repository.save(reference_entity)

        return MembershipBillingReference(
            id=uuid.UUID(stored_entity.id),
            membership_id=uuid.UUID(stored_entity.membership_id),
            external_invoice_id=stored_entity.external_invoice_id,
            external_invoice_reference=stored_entity.external_invoice_reference,
            due_date=stored_entity.due_date,
            status=stored_entity.status,
            created_at=stored_entity.created_at,
            updated_at=stored_entity.updated_at,
        )
