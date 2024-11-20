from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from registration.service import (
    create_registration_session,
    update_registration_session,
    complete_registration_session
)
from registration.schemas import (
    RegistrationSessionUpdate,
    RegistrationSessionResponse
)

router = APIRouter(prefix="/registration", tags=["registration"])

@router.post(
    "/{student_id}",
    response_model=RegistrationSessionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_session(
    student_id: int,
    db: AsyncSession = Depends(get_db)
) -> RegistrationSessionResponse:
    return create_registration_session(db, student_id)

@router.put(
    "/{student_id}",
    response_model=RegistrationSessionResponse
)
async def update_session(
    student_id: int,
    update_data: RegistrationSessionUpdate,
    db: AsyncSession = Depends(get_db)
) -> RegistrationSessionResponse:
    return update_registration_session(db, student_id, update_data.model_dump(exclude_unset=True))

@router.post(
    "/{student_id}/complete",
    response_model=RegistrationSessionResponse
)
async def complete_session(
    student_id: int,
    db: AsyncSession = Depends(get_db)
) -> RegistrationSessionResponse:
    return complete_registration_session(db, student_id) 