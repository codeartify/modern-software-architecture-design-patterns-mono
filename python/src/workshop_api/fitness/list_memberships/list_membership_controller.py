from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.list_memberships.list_membership_response import (
    ListMembershipResponse,
)
from workshop_api.fitness.shared.membership_entity import MembershipOrmModel

router = APIRouter(prefix="/api/memberships", tags=["membership"])


@router.get("", response_model=list[ListMembershipResponse], response_model_by_alias=True)
def list_memberships(
    session: Session = Depends(get_db_session),
) -> list[ListMembershipResponse]:
    memberships = session.query(MembershipOrmModel).all()
    return [ListMembershipResponse.from_entity(membership) for membership in memberships]
