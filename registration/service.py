from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from config import Settings
from utils import generate_uuid
from models import RegistrationStep, RegistrationSession
from registration.schemas import RegistrationSessionResponse

def get_registration_session(
    db: AsyncSession,
    student_id: int
) -> Optional[RegistrationSession]:
    """Fetch active registration session for student"""
    result =  db.execute(
        select(RegistrationSession)
        .where(
            RegistrationSession.student_id == student_id,
            RegistrationSession.expires_at > datetime.now()
        )
    )
    return result.scalar_one_or_none()

def create_registration_session(
    db: AsyncSession,
    student_id: int
) -> RegistrationSessionResponse:
    """Create or return existing registration session"""
    # Check for existing active session
    if existing_session :=  get_registration_session(db, student_id):
        return RegistrationSessionResponse.model_validate(existing_session)

    # Create new session
    new_session = RegistrationSession(
        id=generate_uuid(prefix=Settings.STUDENT_REGISTRATION_SESSION_PREFIX),
        student_id=student_id,
        current_step=RegistrationStep.PERSONAL_INFO,
        completed_steps={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=7)
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return RegistrationSessionResponse.model_validate(new_session)

def update_registration_session(
    db: AsyncSession,
    student_id: int,
    update_data: dict
) -> RegistrationSessionResponse:
    """Update registration session fields"""
    session =  get_registration_session(db, student_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active registration session not found"
        )

    # Update fields
    for field, value in update_data.items():
        setattr(session, field, value)
    
    session.updated_at = datetime.now()
    db.commit()
    db.refresh(session)
    
    return RegistrationSessionResponse.model_validate(session)

def complete_registration_session(
    db: AsyncSession,
    student_id: int
) -> RegistrationSessionResponse:
    """Mark registration session as complete"""
    session =  get_registration_session(db, student_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active registration session not found"
        )

    # Validate all steps are completed
    required_steps = {step.value for step in RegistrationStep if step != RegistrationStep.COMPLETED}
    if not required_steps.issubset(set(session.completed_steps.keys())):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not all registration steps are completed"
        )

    # Mark as completed
    session.completed_steps = {step.value: True for step in RegistrationStep}
    session.current_step = RegistrationStep.COMPLETED
    session.updated_at = datetime.now()
    
    db.commit()
    db.refresh(session)
    
    return RegistrationSessionResponse.model_validate(session)

def reset_registration_session(
    db: AsyncSession,
    student_id: int
) -> bool:
    """Reset a registration session by expiring it"""
    session =  get_registration_session(db, student_id)
    if not session:
        return False

    result =  db.execute(
        select(RegistrationSession)
        .where(RegistrationSession.id == session.id)
    )
    db_session = result.scalar_one_or_none()
    
    if not db_session:
        return False

    db_session.expires_at = datetime.now()
    db.commit()
    
    return True
