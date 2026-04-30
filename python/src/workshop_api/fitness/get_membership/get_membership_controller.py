from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from workshop_api.fitness.database import get_db_session
from workshop_api.fitness.get_membership.get_membership_response import (
    GetMembershipResponse,
)
from workshop_api.fitness.shared.membership_entity import MembershipOrmModel

router = APIRouter(prefix="/api/memberships", tags=["membership"])


@router.get(
    "/{membership_id}",
    response_model=GetMembershipResponse,
    response_model_by_alias=True,
)
def get_membership(
    membership_id: UUID,
    session: Session = Depends(get_db_session),
) -> GetMembershipResponse:
    membership = session.get(MembershipOrmModel, str(membership_id))
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Membership {membership_id} was not found",
        )

    return GetMembershipResponse.from_entity(membership)
