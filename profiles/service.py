from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from models import Student
from profiles.schemas import StudentCreate, StudentUpdate

def get_student_by_id(db: AsyncSession, student_id: int) -> Optional[Student]:
    query = select(Student).where(Student.id == student_id)
    result = db.execute(query)
    return result.scalar_one_or_none()

def get_student_by_email(db: AsyncSession, email: str) -> Optional[Student]:
    query = select(Student).where(Student.email == email)
    result = db.execute(query)
    return result.scalar_one_or_none()

def get_students(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> List[Student]:
    query = select(Student)
    if status:
        query = query.where(Student.status == status)
    query = query.offset(skip).limit(limit)
    result = db.execute(query)
    return result.scalars().all()

def create_student(db: AsyncSession, student: StudentCreate) -> Student:
    # Check if email already exists
    existing_student = get_student_by_email(db, student.email)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    db_student = Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(
    db: AsyncSession,
    student_id: int,
    student_update: StudentUpdate
) -> Student:
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    update_data = student_update.model_dump(exclude_unset=True)
    if update_data.get("email"):
        existing_student = get_student_by_email(db, update_data["email"])
        if existing_student and existing_student.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    for field, value in update_data.items():
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: AsyncSession, student_id: int) -> bool:
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    db.delete(db_student)
    db.commit()
    return True 